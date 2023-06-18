#!/usr/bin/env python3

import aws_cdk as cdk

from codepipeline_cdk_sample.codepipeline_cdk_sample_stack import CodepipelineCdkSampleStack


app = cdk.App()
CodepipelineCdkSampleStack(app, "codepipeline-cdk-sample")

app.synth()
