# import modules
import s3fs
import boto3

def load_to_s3_bucket(df, key, aws_access, aws_secret):
	"""
		load_to_s3_bucket - function to load dataframe data to 
		aws s3 bucket
		df - dataframe
		aws_access - AWS access id
		aws_secret - AWS secret key
	"""
	bucket_name = 'real-yo-realtor-bucket'
	s3 = boto3.client('s3', aws_access_key_id=aws_access,
					  aws_secret_access_key=aws_secret)
	s3.put_object(Body=df.to_csv(
		index=False), Bucket=bucket_name, Key=key)