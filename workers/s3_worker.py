"""
This file is used to interact with S3.
"""
import re
import sys
import random
import string
import boto3
from botocore.exceptions import ClientError, ParamValidationError
from botocore import errorfactory


class S3Worker:
    """
    Class used to interact with S3.
    """
    def __init__(self, bucket_name: str, region_name: str="us-east-1"):
        """
        Class used to interact with S3.
        
        Args:
            bucket_name (str):   Name of the bucket
            region_name (str):   Name of the region
        
        Attributes:
            s3 (object):         Boto3 client object
            bucket (str):        Name of the bucket
        
        Methods:
            upload_file(file_path: str, file_name: str=None)
            list_objects_in_bucket(bucket_name=None)
        
        :Example:
            s3 = S3Worker(bucket_name="my-bucket")
        
        :Example:
            s3 = S3Worker(bucket_name="my-bucket", region_name="us-east-1")
        
        :Example:
            s3 = S3Worker(bucket_name="my-bucket", region_name="us-east-1")
            s3.upload_file("./img/sample.txt", "sample.txt")
        
        :Example: string
            region_name: string
        
        return: None
        
        :Example:
            s3 = S3Worker(bucket_name="my-bucket")
        
        :Example:
            s3 = S3Worker(bucket_name="my-bucket", region_name="us-east-1")
        
        :Example:
            s3 = S3Worker(bucket_name="my-bucket", region_name="us-east-1")
            s3.upload_file("./img/sample.txt", "sample.txt")
        
        :Example:
            s3 = S3Worker(bucket_name="my-bucket", region_name="us-east-1")
            s3.upload_file("./img/sample.txt", "sample.txt")
            s3.list_objects_in_bucket(bucket_name="my-bucket")
        """
        try:
            self.s3 = boto3.client(service_name="s3", region_name=region_name)
            self.s3.head_bucket(Bucket=bucket_name)
            self.bucket = bucket_name
        except ClientError as e:
            sys.exit(f"Could not connect to s3 client or bucket Not Found. Error: {e}")
        except ParamValidationError as e:
            sys.exit(f"Unable to create bucket. Error: {e}")

    def create_bucket(self, bucket_name: str=None, add_random_characters: bool=False):
        """
        Method to create a bucket.

        Args:
            bucket_name (str):   Name of the bucket
        
        return: None
        
        :Example:
            s3 = S3Worker(bucket_name="XXXXXXXXX")
            s3.create_bucket("XXXXXXXXX")
        """
        if bucket_name is None:
            bucket_name = self.bucket
        if add_random_characters is True:
            bucket_name = bucket_name + self.random_string()
        try:
            self.s3.create_bucket(Bucket=bucket_name)
            print(f"Created bucket {bucket_name}")
            self.bucket = bucket_name
        except errorfactory.BucketAlreadyExists as e:
            print(f"Bucket {bucket_name} already exists. \
                  Try changing the bucket name or adding random characters. Error: {e}")

    def list_objects_in_bucket(self, bucket_name=None):
        """
        Method to list objects in a bucket.

        Args:
            bucket_name (str) Optional:   Name of the bucket
        
        return: list
        
        :Example:
            s3 = S3Worker(bucket_name="my_bucket")
            s3.list_objects_in_bucket()
            s3.list_objects_in_bucket(bucket_name="my_bucket")
        """
        if bucket_name is None:
            bucket_name = self.bucket
        response = self.s3.list_objects_v2(Bucket=bucket_name)
        return response.get('Contents', [])

    def object_exists(self, file_name: str):
        """
        Method to check if an object exists in S3.

        Args:
            file_name (str):              Name of the file to check
        
        return: bool
        
        :Example:
            s3 = S3Worker(bucket_name="my-bucket")
            s3.object_exists("sample.txt")
        """
        if self.bucket is None:
            raise ValueError("Bucket name is not set")
        try:
            response = self.s3.head_object(Bucket=self.bucket, Key=file_name)
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                return True
        except ClientError:
            # If file does not exist, return None
            return False

    def upload_file(self, file_path: str, file_name: str=None):
        """
        Method to upload a file to S3.

        Args:
            file_path (str):              The path to the file to upload
            file_name (str) Optional:     Name of the file to upload
        
        return: None
        
        :Example:
            s3 = S3Worker(bucket_name="my-bucket")
            s3.upload_file("./img/sample.txt")
            s3.upload_file("./img/sample.txt", "sample.txt")
        """
        if self.bucket is None:
            raise ValueError("Bucket name is not set")
        # Check if the object already exists
        if self.object_exists(file_name):
            return None
        if file_name is None:
            path=file_path
            pattern = r'[^/]+$'
            file_name = re.search(pattern, path).group()
        try:
            self.s3.upload_file(Filename=file_path, Bucket=self.bucket, Key=file_name)
            return f"https://{self.bucket}.s3.amazonaws.com/data/{file_name}"
        except Exception as e:
            print(f"Could not upload file {file_name} to bucket {self.bucket}. Error: {e}")
            return None

    def write_file_directly_to_s3(self, file_name: str, data: str):
        """
        Method to writes data directly to S3.

        Args:
            file_name (str):              Name of the file to write
            data (str):           Content of the file to write
        
        return: None
        
        :Example:
            s3 = S3Worker(bucket_name="my-bucket")
            s3.write_file_directly_to_s3("sample.txt", "Hello World!")
        """
        if self.bucket is None:
            raise ValueError("Bucket name is not set")
        # Check if the object already exists
        if self.object_exists(file_name):
            print(f"Object {file_name} already exists in bucket {self.bucket}.")
            return None
        try:
            response = self.s3.put_object(Body=data, Bucket=self.bucket, Key=file_name)
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                return {"s3_url": f"https://{self.bucket}.s3.amazonaws.com/data/{file_name}"}
        except Exception as e:
            print(f"Could not write file {file_name} to bucket {self.bucket}. Error: {e}")
            return None

    def random_string(self):
        """
        Generate a random string of 13 characters

        This function generates a random string of 13 characters 
        to use as a unique identifier or filename.

        Returns:
            str: A random string of 13 characters
        """
        # generate 4 digits at random
        nums = random.choices(string.digits, k=4)
        # generate 9 lowercase letters at random
        letters = random.choices(string.ascii_lowercase, k=9)
        # shuffle both nums + letters
        return ''.join(random.sample(nums + letters, 13))

    @staticmethod
    def _renamer(title: str):
        """
        Method used to rename titles

        Args:
            title (str):                 Title of the blog post

        return: str
        """
        # Strip special characters.
        title = re.sub(r'[^\w\s-]', '', title)
        # Convert the title to lowercase and replace spaces with hyphens.
        _ = title.strip().lower()
        new_title = re.sub(r'[-\s]+', '-', _)
        return new_title

    @ staticmethod
    def generate_filename(blog_string, extension=".txt"):
        """
        Generates a filename based on the provided blog string.

        Args:
            blog_string (str):           String to generate filename from
            extension (str):             Extension of the file
        
        return: str
        
        :Example:
            s3 = S3Worker(bucket_name="my-bucket")
            s3.generate_filename("2023-09-24 This is my first! blog?")
        """
        # Split the input string into date and title.
        date, title = blog_string.split(" ", 1)
        return f"{date}-{S3Worker._renamer(title)}{extension}"

if __name__ == "__main__":
    from pprint import pprint

    BUCKET_NAME="Enter my bucket name"
    s3 = S3Worker(BUCKET_NAME)
    pprint(s3.upload_file("../img/sample.txt"))
    for item in s3.list_objects_in_bucket():
        print(item["Key"])
