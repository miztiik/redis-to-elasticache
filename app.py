#!/usr/bin/env python3

from redis_to_elasticache.stacks.back_end.redis_on_ec2_stack import RedisOnEc2Stack
from redis_to_elasticache.stacks.back_end.vpc_stack import VpcStack
from redis_to_elasticache.stacks.back_end.database_migration_prerequisite_stack import DatabaseMigrationPrerequisiteStack
from aws_cdk import core


app = core.App()

env_ORACLE = core.Environment(region="us-east-1")
# env_ORACLE = core.Environment(account="", region="us-east-1")

# VPC Stack for hosting Secure API & Other resources
vpc_stack = VpcStack(
    app,
    f"{app.node.try_get_context('service_name')}-vpc-stack",
    description="Miztiik Automation: VPC to host resources for DB Migration",
    env=env_ORACLE
)

# Build the pre-reqs for MSSQL on EC2
database_migration_stack = DatabaseMigrationPrerequisiteStack(
    app,
    f"{app.node.try_get_context('service_name')}-database-migration-prerequisite-stack",
    stack_log_level="INFO",
    vpc=vpc_stack.vpc,
    description="Miztiik Automation: DMS Best Practice Demonstration. This stack will create roles and security groups to assist in database migration",
    env=env_ORACLE
)


# Source Database: Redis on EC2
redis_on_ec2_stack = RedisOnEc2Stack(
    app,
    f"{app.node.try_get_context('service_name')}-redis-on-ec2-stack",
    vpc=vpc_stack.vpc,
    ec2_instance_type="m5.large",
    ssh_key_name=database_migration_stack.custom_ssh_key_name,
    stack_log_level="INFO",
    description="Miztiik Automation: Source Database: Redis on EC2",
    env=env_ORACLE
)


# Stack Level Tagging
core.Tag.add(app, key="Owner",
             value=app.node.try_get_context("owner"))
core.Tag.add(app, key="OwnerProfile",
             value=app.node.try_get_context("github_profile"))
core.Tag.add(app, key="Project",
             value=app.node.try_get_context("service_name"))
core.Tag.add(app, key="GithubRepo",
             value=app.node.try_get_context("github_repo_url"))
core.Tag.add(app, key="Udemy",
             value=app.node.try_get_context("udemy_profile"))
core.Tag.add(app, key="SkillShare",
             value=app.node.try_get_context("skill_profile"))
core.Tag.add(app, key="AboutMe",
             value=app.node.try_get_context("about_me"))
core.Tag.add(app, key="BuyMeACoffee",
             value=app.node.try_get_context("ko_fi"))
app.synth()
