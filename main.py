"""
Gets blog posts and stores in Amazon s3
"""
from workers.blog_worker import BlogPost
from workers.s3_worker import S3Worker


def main(aws_blog_home_url: str, bucket_name: str) -> str:
    """
    Process AWS blogs from a aws_blog_home_url and save to S3.

    This function takes a URL pointing to a list of AWS blog 
    posts and a S3 bucket name. It will retrieve each blog 
    post, extract the metadata and body, generate a filename,
    and save the file directly to the S3 bucket.

    Args:
        aws_blog_home_url (str):            The URL of the AWS blog list 
        bucket_name (str):                  The name of the S3 bucket to save files

    Returns: 
        blog_list (list):                   The list of processed blog dictionaries

    """
    worker = BlogPost()
    s3 = S3Worker(bucket_name)
    blog_list = get_aws_blogs_list(worker, aws_blog_home_url)
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
        s3.write_file_directly_to_s3(file_name=blog_title, data=blog_body)
        i += 1
        print(f"{str(i)}. {blog_title}")
    print(f"Completed successfully.\nTotal number of blogs: {str(i)}")
    return blog_list

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
        title =  blog_title + " " + date_published
    else:
        raise ValueError("date_published and blog_title are required.")
    s3_file_name = S3Worker.generate_filename(title)
    return s3_file_name

def get_aws_blogs_list(aws_blog_worker: BlogPost, aws_blog_home_url: str) -> list:
    """
    Gets a list of aws blog urls.

    Args:
        aws_blog_worker (BlogPost):     BlogPost object
        aws_blog_home_url (str):        The URL of the AWS blog list 
    Returns:
        list: list of aws blog urls
    """
    next_page = aws_blog_home_url
    worker = aws_blog_worker
    seen_pages = []
    # Compiles a list of aws blog urls
    while next_page:
        seen_pages.append(next_page)
        soup = worker.get_soup(next_page)
        if soup:
            worker.get_all_url_links_on_page(soup)
            next_page = worker.check_pagination(soup)
            if next_page in seen_pages:
                break

    return aws_blog_worker.links


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Process AWS blogs from an AWS Blog Home and save to S3.")
    parser.add_argument("--aws_blog_home_url", help="The URL of the AWS blog list. \
                        Ex: https://aws.amazon.com/blogs/networking-and-content-delivery/")
    parser.add_argument("--bucket_name", help="The name of the S3 bucket to save files")
    args = parser.parse_args()
    main(args.aws_blog_home_url, args.bucket_name)
