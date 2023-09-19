from blog_worker import BlogPost


def main(url: str) -> str:
    current_url = url
    worker = BlogPost()
    i = 0
    temp = []
    soup = worker.get_soup(current_url)
    # Compiles a list of aws blog urls -> worker.network_content_delivery_links
    while current_url:
        temp.append(current_url)
        soup = worker.get_soup(current_url)
        if soup:
            worker.get_all_url_links_on_page(soup)
            current_url = worker.check_pagination(soup)
            if current_url in temp:
                break
    aws_blog_urls = worker.network_content_delivery_links
    # Takes the aws blog urls and gets the data about each blog and returns a list of dictionaries
    post_data_list = []
    for blog_url in aws_blog_urls:
        soup = worker.get_soup(blog_url)
        post_data_list.append(worker.get_blog_dict(soup))
    return post_data_list

# GETS SOME ATTRIBUTE DATA ABOUT THE BLOG POSTS
def sample(url: str) -> list:
    worker = BlogPost()
    soup = worker.get_soup(url)
    return worker.get_blog_dict(soup)
   
if __name__ == "__main__":
    from pprint import pprint
    url = "https://aws.amazon.com/blogs/networking-and-content-delivery/use-bring-your-own-ip-addresses-byoip-and-rfc-8805-for-localization-of-internet-content/"
    data = sample(url)
    print(data)
    #url = "https://aws.amazon.com/blogs/networking-and-content-delivery/"
    #soup = main(url)
    #print(soup)
    #pprint(summary)
