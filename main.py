from workers.blog_worker import BlogPost
from workers.db_worker import DynamoDBWorker
from workers.s3_worker import S3Worker
from dotenv import load_dotenv
import os

load_dotenv()

BUCKET_NAME = os.getenv("BUCKET_NAME")
TABLE_NAME = "blog_posts"


def main(url: str=None) -> str:
    worker = BlogPost()
    s3 = S3Worker(BUCKET_NAME)
    #db = DynamoDBWorker(TABLE_NAME)
    # Gets a list of all AWS Networking and Content Delivery blogs
    blog_list = get_aws_blogs_list(worker, url)
   
    # Takes the aws blog urls and gets the data about each blog and returns a list of dictionaries

    i =0
    for blog in blog_list:
        # Gets the soup of the blog
        soup = worker.get_soup(blog)
        # Gets the blog dict meta-data
        blog_dict = worker.get_blog_dict(soup)
        # Generates a string for the S3 file name
        blog_title = get_title_string(blog_dict)
        # Gets the blog body
        blog_body = worker.get_blog_body(soup)
        # Writes the blog body to S3
        s3_url = s3.write_file_directly_to_s3(file_name=blog_title, data=blog_body)
        # Adds the s3 url of blog to the blog_dict of meta-data
        #blog_dict["s3_url"] = s3_url
        # Writes the blog dict to DynamoDB
        #db.post_item(blog_dict)
        i += 1
        print(f"{str(i)}. {blog_title}")
    return "Completed successfully"

def get_title_string(blog_dict: dict) -> str:
    """
    Generates a string for the S3 file name.

    Args:
        blog_dict (dict):       blog dict
    Returns:
        str: s3 file name string.
    """
    date_published = blog_dict.get("date_published", None)
    blog_title = blog_dict.get("blog_title", None)
    if date_published and blog_title:
        title = date_published + " " + blog_title
    else:
        raise ValueError("date_published and blog_title are required.")
    s3_file_name = S3Worker.generate_filename(title)
    return s3_file_name

def get_aws_blogs_list(aws_blog_worker: BlogPost, url: str) -> list:
    """
    Gets a list of aws blog urls.

    Args:
        aws_blog_worker (BlogPost):  BlogPost object
    Returns:
        list: list of aws blog urls
    """
    current_url = "https://aws.amazon.com/blogs/networking-and-content-delivery/"
    worker = aws_blog_worker
    temp = []
    soup = worker.get_soup(url)
    # Compiles a list of aws blog urls -> worker.network_content_delivery_links
    while current_url:
        temp.append(current_url)
        soup = worker.get_soup(current_url)
        if soup:
            worker.get_all_url_links_on_page(soup)
            current_url = worker.check_pagination(soup)
            if current_url in temp:
                break
    
    return aws_blog_worker.network_content_delivery_links
   
if __name__ == "__main__":
    from pprint import pprint
    #url = "https://aws.amazon.com/blogs/networking-and-content-delivery/use-bring-your-own-ip-addresses-byoip-and-rfc-8805-for-localization-of-internet-content/"
    url = "https://aws.amazon.com/blogs/networking-and-content-delivery/"
    soup = main(url)
    pprint(soup[0])
    print(len(soup))
