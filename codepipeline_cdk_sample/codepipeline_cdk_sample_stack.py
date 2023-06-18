from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    SecretValue,
    aws_codecommit as codecommit,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
)

class CodepipelineCdkSampleStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        DEPLOY_STACK_NAME = "TestApiStack"
        CHANGE_SET_NAME = "TestApiStackChangeSet"

        ####################
        # CodeCommit
        ####################
        # CodeCommitリポジトリの作成
        repo = codecommit.Repository(
            self,
            "kotasuzuki-test",
            repository_name="kotasuzuki-test"
        )


        ####################
        # CodeBuild
        ####################

        # buildspecの定義
        buildspec = {
            "version": "0.2",
            "phases": {
                "install": {
                    "runtime-versions":{
                        "python": "3.10"
                    },
                    "commands":[
                        "python3 -m pip install pipenv",
                        "npm install -g aws-cdk",
                        "pipenv install",
                    ]
                },
                "pre_build":{
                    "commands": [
                        "echo pre_build stage."
                    ]
                },
                "build": {
                    "commands": [
                        # Python virtual environments
                        "echo Launching virtual environments started..",
                        "export VENV_HOME_DIR=$(pipenv --venv)",
                        ". $VENV_HOME_DIR/bin/activate",
                        
                        "cdk synth",
                    ]
                }
            },
            "artifacts": {
                "base-directory": "cdk.out",
                "files": "**/*"
            },
        }

        # ビルドプロジェクトの作成
        build_project = codebuild.PipelineProject(
            self,
            id="sample_build_project",
            project_name="sample_build_project",
            build_spec=codebuild.BuildSpec.from_object(buildspec),
            # コンテナの設定
            environment=codebuild.BuildEnvironment(
                # python3.10はstandard:6.0のみ対応
                build_image=codebuild.LinuxBuildImage.STANDARD_6_0,
                compute_type=codebuild.ComputeType.SMALL,
                privileged=True
            ),
            timeout=Duration.minutes(10)
        )

        # Buildプロジェクトの成果物（アーティファクト）
        output_data = codepipeline.Artifact("output_data")


        ####################
        # CodePipeline
        ####################

        # パイプラインの定義
        pipeline = codepipeline.Pipeline(
            self,
            id="sample_pipeline",
            pipeline_name="sample_pipeline"
        )

        # ================ source stage ================

        # 取り込むGitのブランチ
        branch = "master"

        # Gitのアウトプット先の設定（アーティファクト）
        source_output = codepipeline.Artifact("source_output")

        # CodeCommitに接続
        source_action = codepipeline_actions.CodeCommitSourceAction(
            action_name="CodeCommit_Source",
            repository=repo,
            branch=branch,
            trigger=codepipeline_actions.CodeCommitTrigger.POLL,
            output=source_output
        )

        # Githubの場合(SSMで認証トークンの設定が必要)
        # github_repository_name = "aws-cdk-repo"
        # source_action = codepipeline_actions.GitHubSourceAction(
        #     action_name="GitHub_Source",
        #     owner="awslabs",
        #     repo=github_repository_name,
        #     oauth_token=SecretValue.secrets_manager("my-github-token"),
        #     output=source_output,
        #     branch=branch
        # )

        # pipelineにステージ追加
        pipeline.add_stage(
            stage_name="Source",
            actions=[source_action]
        )

        # ================ build stage ================

        # CodeBuildをステージに追加
        build_action = codepipeline_actions.CodeBuildAction(
            action_name="build_action",
            project=build_project,
            input=source_output,
            outputs=[output_data]
        )

        # Buildステージの追加
        pipeline.add_stage(
            stage_name="Build",
            actions=[build_action]
        )

        # ============ deploy stage start ============

        # デプロイ時に使用するCFnテンプレートファイル名
        template = "hoge.template.json"
        
        # CloudFormationによるデプロイ
        pipeline.add_stage(
            stage_name="CloudFormation_Deploy",
            actions=[
                codepipeline_actions.CloudFormationCreateReplaceChangeSetAction(
                    action_name="CreateCFnChangeSet",
                    admin_permissions=True,
                    stack_name=DEPLOY_STACK_NAME,
                    change_set_name=CHANGE_SET_NAME,
                    template_path=output_data.at_path(template),
                    run_order=1
                ),
                codepipeline_actions.ManualApprovalAction(
                    action_name="Review",
                    run_order=2
                ),
                codepipeline_actions.CloudFormationExecuteChangeSetAction(
                    action_name="DeployResources",
                    stack_name=DEPLOY_STACK_NAME,
                    change_set_name=CHANGE_SET_NAME,
                    run_order=3
                ),
            ]
        )

