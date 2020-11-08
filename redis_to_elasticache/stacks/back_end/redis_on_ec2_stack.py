from aws_cdk import aws_ec2 as _ec2
from aws_cdk import aws_iam as _iam
from aws_cdk import core


class GlobalArgs():
    """
    Helper to define global statics
    """

    OWNER = "MystiqueAutomation"
    ENVIRONMENT = "production"
    REPO_NAME = "mysql-to-rds"
    SOURCE_INFO = f"https://github.com/miztiik/{REPO_NAME}"
    VERSION = "2020_10_24"
    MIZTIIK_SUPPORT_EMAIL = ["mystique@example.com", ]


class RedisOnEc2Stack(core.Stack):

    def __init__(
        self,
        scope: core.Construct, id: str,
        vpc,
        ec2_instance_type: str,
        ssh_key_name: str,
        stack_log_level: str,
        **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Read BootStrap Script):
        try:
            with open("redis_to_elasticache/stacks/back_end/bootstrap_scripts/deploy_app.sh",
                      encoding="utf-8",
                      mode="r"
                      ) as f:
                user_data = f.read()
        except OSError as e:
            print("Unable to read UserData script")
            raise e

        # Get the latest AMI from AWS SSM
        linux_ami = _ec2.AmazonLinuxImage(
            generation=_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2)

        # Get the latest ami
        amzn_linux_ami = _ec2.MachineImage.latest_amazon_linux(
            generation=_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
        )
        # ec2 Instance Role
        _instance_role = _iam.Role(
            self, "webAppClientRole",
            assumed_by=_iam.ServicePrincipal(
                "ec2.amazonaws.com"),
            managed_policies=[
                _iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSSMManagedInstanceCore"
                )
            ]
        )

        # Allow CW Agent to create Logs
        _instance_role.add_to_policy(_iam.PolicyStatement(
            actions=[
                "logs:Create*",
                "logs:PutLogEvents"
            ],
            resources=["arn:aws:logs:*:*:*"]
        ))

        # db_server Instance
        db_server = _ec2.Instance(
            self,
            "dbServer",
            instance_type=_ec2.InstanceType(
                instance_type_identifier=f"{ec2_instance_type}"),
            instance_name="Redis_Db",
            machine_image=amzn_linux_ami,
            vpc=vpc,
            vpc_subnets=_ec2.SubnetSelection(
                subnet_type=_ec2.SubnetType.PUBLIC
            ),
            role=_instance_role,
            user_data=_ec2.UserData.custom(
                user_data)
        )

        # Allow Web Traffic to WebServer
        db_server.connections.allow_from_any_ipv4(
            _ec2.Port.tcp(80),
            description="Allow Incoming HTTP Traffic"
        )

        # db_server.connections.allow_internally(
        #     port_range=_ec2.Port.tcp(3306),
        #     description="Allow Incoming MySQL Traffic"
        # )

        db_server.connections.allow_from(
            other=_ec2.Peer.ipv4(vpc.vpc_cidr_block),
            port_range=_ec2.Port.tcp(6379),
            description="Allow Incoming Elasticache Traffic"
        )

        # Allow CW Agent to create Logs
        _instance_role.add_to_policy(_iam.PolicyStatement(
            actions=[
                "logs:Create*",
                "logs:PutLogEvents"
            ],
            resources=["arn:aws:logs:*:*:*"]
        ))

        ###########################################
        ################# OUTPUTS #################
        ###########################################
        output_0 = core.CfnOutput(
            self,
            "AutomationFrom",
            value=f"{GlobalArgs.SOURCE_INFO}",
            description="To know more about this automation stack, check out our github page."
        )
        output_1 = core.CfnOutput(
            self,
            "RedisPrivateIp",
            value=f"http://{db_server.instance_private_ip}",
            description=f"Private IP of Redis on EC2"
        )
        output_2 = core.CfnOutput(
            self,
            "RedisInstance",
            value=(
                f"https://console.aws.amazon.com/ec2/v2/home?region="
                f"{core.Aws.REGION}"
                f"#Instances:search="
                f"{db_server.instance_id}"
                f";sort=instanceId"
            ),
            description=f"Login to the instance using Systems Manager and use curl to access the Redis Instance"
        )
