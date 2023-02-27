import boto3
import json

# Prompt the user for AWS credentials
aws_access_key_id = input("Enter AWS access key ID: ")
aws_secret_access_key = input("Enter AWS secret access key: ")
aws_session_token = input("Enter AWS session token (optional, press enter if not needed): ")

# Specify the mandatory tags
mandatory_tags = ["Name", "Environment", "Team"]

# Create a session using the AWS credentials and region
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    aws_session_token=aws_session_token
)

# Get a clist of all AWS regions
ec2_client = session.client("ec2", region_name="us-east-1")
regions = [region["RegionName"] for region in ec2_client.describe_regions()["Regions"]]

# Create an empty list to store the instances and S3 buckets with the mandatory tags
instances_with_tags = []
buckets_with_tags = []

# Check each region for instances and S3 buckets with the mandatory tags
for region in regions:
    ec2 = session.resource("ec2", region_name=region)
    s3 = session.resource("s3", region_name=region)

    # Check instances with mandatory tags
    instances = ec2.instances.filter(Filters=[{"Name": "instance-state-name", "Values": ["running"]}])
    for instance in instances:
        tags = {tag["Key"]: tag["Value"] for tag in instance.tags or []}
        if all(tag in tags for tag in mandatory_tags):
            instances_with_tags.append({
                "InstanceID": instance.id,
                "Region": region,
                "Tags": tags
            })

    # Check S3 buckets with mandatory tags
    buckets = s3.buckets.all()
    for bucket in buckets:
        tags = bucket.Tagging().tag_set or []
        tag_dict = {tag["Key"]: tag["Value"] for tag in tags}
        if all(tag in tag_dict for tag in mandatory_tags):
            buckets_with_tags.append({
                "BucketName": bucket.name,
                "Region": region,
                "Tags": tag_dict
            })

# Print the instances and S3 buckets with the mandatory tags in JSON format
print(json.dumps({"InstancesWithTags": instances_with_tags, "BucketsWithTags": buckets_with_tags}))
