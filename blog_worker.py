"""
Gets Blog Posts data and summarizes it
"""
import requests
from bs4 import BeautifulSoup
import sys


# Create a class that will be used to gather filter and return blog posts from websites
class BlogPost:
    def __init__(self):
        self.url = None
        self.network_content_delivery_links = []
 
    def get_soup(self, url=None) -> BeautifulSoup:
        """
        Gets the soup of the website
        
        Args:
            url (str): url of the website

        Returns:
            BeautifulSoup: soup of the website
        """
        response = requests.get(url)
        if response.status_code != 200:
            print("Error: Could not get the soup of the website")
            return None
        else:
            self.url = url  
            return BeautifulSoup(response.text, "html.parser")

    def get_all_url_links_on_page(self, soup=BeautifulSoup):
        """
        Gets all urls from https://aws.amazon.com/blogs/networking-and-content-delivery/
        
        Args:
            soup (BeautifulSoup): soup of the website

        Returns:
            list: list of all urls on a page
        """
        links = soup.find_all("h2", {"class": "lb-bold blog-post-title"})
        for link in links:
            self.network_content_delivery_links.append(link.find("a").get("href"))
    
    def check_pagination(self, soup=BeautifulSoup):
        """
        Checks for pagination and returns the next url
        
        Args:
            soup (BeautifulSoup): soup of the website

        Returns:
            str: next url
        """
        try:
            pages = soup.find_all("div", {"class": "blog-pagination"})
            if pages:
                for page in pages:
                    url = page.find("a").get("href")
                    if "page" in url:
                        return url
                    else:
                        return None
            else:
                return None
        except NameError as e:
            print(e)
            exit()
    
    def get_blog_body(self, soup=BeautifulSoup):
        """
        GETS the body of a blog post
        
        Args:
            soup (BeautifulSoup): soup of the website

        Returns:
            str: body of a blog post
        """
        for div in soup.find_all("footer", {"class": "blog-post-meta"}):
            div.decompose()
        for div in soup.find_all("div", {"class": "blog-author-box"}):
            div.decompose()
        return soup.article.get_text().strip()

    def get_blog_dict(self, soup=BeautifulSoup) -> dict:
        """
        Returns the blog dict
        
        Returns:
            dict: blog attributes as a dict
        """
        authors = []
        blog_tags = []
        category = soup.find("h2", {"class": "lb-h5 blog-title"}).get_text().strip()
        # Get Blog Post title
        blog_title = soup.find("h1", {"class": "lb-h2 blog-post-title"}).get_text().strip()
        # Get authors from post
        for author in soup.find_all("h3", {"class": "lb-h4"}):
            if author:
                authors.append(author.get_text().strip())
        for author in soup.find_all("span", {"property": "author"}):
            if author:
                if author not in authors:
                    authors.append(author.get_text().strip())
            
        # Get Published date
        today = soup.find("time", {"property": "datePublished"}).get_text().strip()
        # Get tags from post
        blog_title_tags = soup.find("span", {"class": "blog-post-categories"}).get_text().strip().lower() + f", {blog_title.lower()}"
        aws_tags = self.get_tags(blog_title_tags)
        # Get all tags and add them to list
        for div in soup.find_all("div", {"class":"blog-tag-list"}):
            if "TAGS: " in div.get_text().strip():
                blog_tags.append(div.extract().get_text().strip()[15:])
            else:
                blog_tags.append(div.extract().get_text().strip())
        if blog_tags:
            for tag in blog_tags:
                if tag.lower() not in aws_tags:
                    aws_tags.append(tag.lower())
        post_data = {
                'category': category,
                'title': blog_title,
                'authors': list(set(authors)),
                'date': today,
                'tags': list(set(aws_tags)),
                'url': self.url
            }
        return post_data
            

    ## Get tags from text file.
    def get_tags(self, blog_title_tags: list) -> list:
        """
        GETS list of blog tags
        
        Args:
            blog_title_tags (list): list of tags from blog title

        Returns:
            list: list of tags
        """
        tags = []
        with open('aws_services.txt') as f:
            lines = [line.rstrip().lower() for line in f]
            for tag in lines:
                if tag in blog_title_tags:
                    tags.append(tag)
            return tags
