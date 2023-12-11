import boto3
import logging
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

# Setup logging
logging.basicConfig(filename='./logs/app.log', filemode='a', format='%(asctime)s - - %(module)s - %(levelname)s - %(message)s', level=logging.INFO)

class DynamoDBWorker:
    """Encapsulates an Amazon DynamoDB table of blog post."""
    def __init__(self, table_name, region_name="us-east-1"):
        self.dynamodb = boto3.resource(service_name='dynamodb', region_name=region_name)
        self.table_name = table_name
        self.table = self.get_or_create_table()

    def _table_exists(self):
        try:
            tables = [table.name for table in self.dynamodb.tables.all()]
            if self.table_name in tables:
                return True
        except ClientError as e:
            logging.error(e)
            return False

    def get_or_create_table(self):
        if self._table_exists():
            logging.info(f"Table {self.table_name} already exists.")
            return self.dynamodb.Table(self.table_name)
        else:
            return self.create_table()

    def create_table(self):
        """
        Creates an Amazon DynamoDB table that can be used to store blog posts.
        The table uses the aws as the partition key and the
        category as the sort key.

        :return: The newly created table.
        """
        logging.info(f"Creating table {self.table_name}.")
        try:
            table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {'AttributeName': 'blog_title', 'KeyType': 'HASH'},
                    {'AttributeName': 'date_published', 'KeyType': 'RANGE'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'blog_title', 'AttributeType': 'S'},
                    {'AttributeName': 'date_published', 'AttributeType': 'S'},
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
            table.meta.client.get_waiter('table_exists').wait(TableName=self.table_name)
            logging.info(f"Table {self.table_name} created successfully.")
            return table
        except ClientError as e:
            logging.error(f"Could not create table. Error: {e}")

    def post_item(self, item):
        """
        Method to post an item to the DynamoDB table.

        Args:
            item (dict):            The item to post.
        
        """
        try:
            self.table.put_item(
                Item=item,
                ConditionExpression=Attr('blog_title').not_exists()
            )
            logging.info(f"Item posted: {item}")
        except ClientError as e:
            logging.error(f"Could not post item. Error: {e}")
        

    def search_items(self, attribute, value, index_name=None):
        try:
            if index_name:
                # Query using Global Secondary Index
                return self.table.query(
                    IndexName=index_name,
                    KeyConditionExpression=f"{attribute} = :v",
                    ExpressionAttributeValues={':v': value}
                )['Items']
            
            elif attribute == 'blog_title' or attribute == 'date_published':
                # Query using primary key or sort key
                return self.table.query(
                    KeyConditionExpression=f"{attribute} = :v",
                    ExpressionAttributeValues={':v': value}
                )['Items']
                
            else:
                # Perform a scan for other attributes (inefficient on large tables)
                return self.table.scan(
                    FilterExpression=f"{attribute} = :v",
                    ExpressionAttributeValues={':v': value}
                )['Items']
                
        except Exception as e:
            logging.info(f"Failed to search items by {attribute}: {e}")
            return None
