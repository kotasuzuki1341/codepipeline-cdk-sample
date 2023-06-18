# codepipeline-cdk-sample

## 概要
CDKのソースコードをCloudFormationテンプレートに変換しデプロイするためのCodePipelineのパイプライン


## パイプラインのステージについて

### Sourceステージ
GitHubもしくはCodeCommitの指定したリポジトリ・ブランチからコードをインポートする。<br>
CodeCommitの場合はこのCDKで作成されるリポジトリが指定されている。

### Buildステージ
CodeBuildを使用している。buildspecはPython仮想環境の作成及びCDKフレームワークで書かれたコードからCloudFormationテンプレートに変換する処理が記載されている。

### Deployステージ
このステージには、3つの処理が実装されている。

#### CreateCFnChangeSet
Buildステージで作成されたテンプレートを基に、チェンジセットを作成する

#### Review
承認処理を実施

#### DeployResources
チェンジセットを基にスタックのデプロイを実行

デプロイ先は基本的にこのパイプラインが実行されているAWSアカウントの東京リージョン（ap-northeast-1）である。