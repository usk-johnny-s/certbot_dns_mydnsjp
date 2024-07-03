# Certbot DNS MyDNS.JP Plugin
This is an authenticator plugin for certbot to handle dns-01 challenge with MyDNS.JP.

[日本語の説明はこちら](#Japanese)

## Reference
[*MyDNS.JP*](https://www.mydns.jp/) free DynamicDNS, free subdomains, and you can also set a fixed IP address or your owned domain.

[*Let's Encript*](https://letsencrypt.org/ja/) Free SSL/TLS certificate (DV certificate), Wildcard certificate can be issued using DNS-01 challenge.

[*certbot*](https://github.com/certbot/certbot) ACME client recommended by Let's Encript, challenge authentication processing can be added with plugins.

## Install
To install this plugin, please perform one of the installation steps below.

Please note that certbot is required to run the plugin. Please check [the certbot documentation](https://eff-certbot.readthedocs.io/en/latest/install.html) for certbot installation instructions.

### snap
Add the plugin using snap to certbot installed using snap.
```commandline
snap install certbot-dns-mydnsjp
snap set certbot trust-plugin-with-root=ok
snap connect certbot:plugin certbot-dns-mydnsjp
snap connect certbot-dns-mydnsjp:certbot-metadata certbot:certbot-metadata
```

### Docker
Get a pre-built image (including certbot).
```commandline
docker image pull uskjohnnys/certbot-dns-mydnsjp
```

### pip
Add the plugin with pip to certbot installed with pip.
```commandline
pip install certbot-dns-mydnsjp
```

### from source code
Add the plugin using pip from the source code to certbot installed using pip.
```commandline
git clone https://github.com/usk-johnny-s/certbot_dns_mydnsjp
cd certbot_dns_mydnsjp
pip install .
```

## Check if the plugin is recognized
```commandline
certbot plugins
```
If "dns-mydnsjp" is displayed in the plugin list, this plugin is recognized.

If it is not recognized, certbot included in the OS package may not be uninstalled. Please uninstall the plugin and certbot and then perform the installation steps again.

## How to use

### Creating a MyDnsJp account settings file
Please register your account with MyDNS.JP in advance and register the domain name in your account.

Enter the registered domain name and account information in the MyDnsJp account settings file (e.g. mydnsjp.ini). The created MyDnsJp account configuration file prohibits Other access (for example, chmod 660 mydnsjp.ini). (Suppressing warnings when running certbot)
```ini
[dns_mydnsjp_credential]
[[example.mydns.jp]]
'id'='mydns_jp_mastrid'
'pwd'='mydns_jp_masterpassword'
```
MyDNS.JP can also register host names that include dots, such as "A.example," so if domain zone separation is not required, you can also obtain a certificate for A.example.mydns.jp using the above configuration file. (If you do not separate zones, there is no need to delegate subdomains to child accounts.)

If you log in to MyDNS.JP and register on the DOMAIN INFO screen with TargetID=child account in the host record, that record will be the IP notified by the child account.

To perform zone separation for subdomains on MyDNS.JP, log in to MyDNS.JP and add a child account on the USER INFO screen, then log in to MyDNS.JP and on the DOMAIN INFO screen, select "Hostname=Sublevel". You can delegate a subdomain to a child account by setting the domain name, Type=DELEGATE, TargetID=child account.

If you want to obtain certificates for both the parent account's domain and the child account's subdomain, please include the authentication information for both the parent account and child account in the MyDnsJp account configuration file.
```ini
[dns_mydnsjp_credential]
[[example.mydns.jp]]
'id'='mydns_jp_masterid'
'pwd'='mydns_jp_masterpassword'
[[sub.example.mydns.jp]]
'id'='mydns_jp_childid'
'pwd'='mydns_jp_childpassword'
…
```

MyDNS.JP allows you to register one domain with one account. (If you want to register multiple domains with MyDNS.JP, register multiple accounts.) If you list multiple domains in the MyDnsJp account settings file, you can also obtain multi-domain certificates using MyDNS.JP. can.
```ini
[dns_mydnsjp_credential]
[[example1.mydns.jp]]
'id'='mydns_jp_mastrid1'
'pwd'='mydns_jp_masterpassword1'
[[example2.mydns.jp]]
'id'='mydns_jp_masterid2'
'pwd'='mydns_jp_masterpassword2'
…
```

## Execute certbot
Run the DNS-01 challenge on MyDNS.JP by adding the following to the certbot command line option. (Check the certbot page for other options.)
```commandline
certbot \
  --preferred-challenges dns \
  --authenticator dns-mydnsjp \
  --dns-mydnsjp-credentials <MyDNS account configuration file (e.g. mydns.ini)>
  …
```

If an error occurs while running certbot, deletion/restoration of the DNS TXT record after authentication may fail,
so please log in to MyDNS.JP and delete/modify the record contents on the DOMAIN INFO screen.

(The TXT record used for DNS-01 challenge authentication is a TXT record whose hostname starts with "_acme-challenge".)

### Plugin command line options
| Options | Functions/Applications |
|:---:|:---:|
| --dns-mydns-propagation-seconds <number of seconds to wait> | Wait time after DNS configuration (seconds) Default=30 |
| --dns-mydns-credentials <MyDNS account configuration file name> | Specify the file name that describes the MyDnsJp account |
| --dns-mydns-no-txt-restore | NS-01 challenge Delete the TXT entry used after authentication (if this option is not specified: restore the used TXT entry) |

## Build the package
If you need to rebuild the package, please refer to the build instructions below.

### Building the snap package
[Install snapcraft](https://snapcraft.io/docs/create-a-new-snap), then run the following:
````command line
git clone https://github.com/usk-johnny-s/certbot_dns_mydnsjp
cd certbot_dns_mydnsjp
snapcraft
````

### Building the Docker image
[Install Docker](https://docs.docker.com/get-docker/), then run the following:
````command line
git clone https://github.com/usk-johnny-s/certbot_dns_mydnsjp
cd certbot_dns_mydnsjp
docker build -t certbot-dns-mydnsjp:local .
````

### Building the Python package
[Install setuptools](https://setuptools.pypa.io/en/latest/userguide/quickstart.html), then run the following:
````command line
git clone https://github.com/usk-johnny-s/certbot_dns_mydnsjp
cd certbot_dns_mydnsjp
python -m build
````

## Thanks to

[*disco-v8/DirectEdit*](https://github.com/disco-v8/DirectEdit) MyDNS.JP genuine DNS authentication script. It was not suitable for my purpose of ``subdomain + multidomain without zone separation'', which led me to develop this plugin.


[*infinityofspace/certbot_dns_duckdns*](https://github.com/infinityofspace/certbot_dns_duckdns) A very simple DNS authentication plugin for certbot. I referenced it as a source code skeleton when developing this plugin.

---
---

# Certbot DNS MyDNS.JP プラグイン (Japanese)<a name="Japanese"></a>

MyDNS.JPでdns-01チャレンジを処理するためのcertbot用の認証プラグインです。

## 参照
[*MyDNS.JP*](https://www.mydns.jp/) 無料で利用できるDynamicDNS、無料のサブドメインも利用可能、固定IPアドレスや自分の保有するドメインも設定可能

[*Let's Encript*](https://letsencrypt.org/ja/) 無料で利用できるSSL/TLS証明書(DV証明書)、DNS-01 challengeを使用すればワイルドカード証明書が発行可能

[*certbot*](https://github.com/certbot/certbot) Let's Encriptが推奨しているACMEクライアント、プラグインでchallenge認証処理を追加可能

## インストール
このプラグインのインストールは、下記インストール手順のうち、いずれか１つを実行してください。

なお、プラグインの実行にはcertbotが必要です。
certbotのインストール手順は[certbotのドキュメント](https://eff-certbot.readthedocs.io/en/latest/install.html)を確認してください。

### snap
snapでインストールしたcertbotに、snapでプラグインを追加。
```commandline
snap install certbot-dns-mydnsjp
snap set certbot trust-plugin-with-root=ok
snap connect certbot:plugin certbot-dns-mydnsjp
snap connect certbot-dns-mydnsjp:certbot-metadata certbot:certbot-metadata
```

### Docker
ビルド済みイメージ(certbotを含む)を取得。
```commandline
docker image pull uskjohnnys/certbot-dns-mydnsjp
```

### pip
pipでインストールしたcertbotに、pipでプラグインを追加。
```commandline
pip install certbot-dns-mydnsjp
```

### ソースコードからインストール
pipでインストールしたcertbotに、ソースコードからpipでプラグインを追加。
```commandline
git clone https://github.com/usk-johnny-s/certbot_dns_mydnsjp
cd certbot_dns_mydnsjp
pip install .
```

## プラグインを認識しているかの確認
```commandline
certbot plugins
```
プラグインの一覧に「dns-mydnsjp」が表示されていれば、このプラグインを認識しています。

認識していない場合は、OSパッケージに含まれたcertbotがアンインストールできていない可能性があります。
プラグインとcertbotをアンインストールしてから、再度インストール手順を実施してください。

## 使用方法

### MyDnsJpアカウント設定ファイルの作成
事前にMyDNS.JPでアカウント登録を行い、アカウントにドメイン名を登録しておいてください。

登録したドメイン名とアカウント情報をMyDnsJpアカウント設定ファイル(例:`mydnsjp.ini`)に記載します。
作成したMyDnsJpアカウント設定ファイルはOtherアクセスを禁止(例:`chmod 660 mydnsjp.ini`)しておきます。(certbot実行時の警告抑止)
```ini
[dns_mydnsjp_credential]
[[example.mydns.jp]]
'id'='mydns_jp_mastrid'
'pwd'='mydns_jp_masterpassword'
```
MyDNS.JPは「A.example」などドットを含むホスト名も登録できますので、
ドメインのゾーン分離が不要であれば上記設定ファイルでA.example.mydns.jpの証明書も取得できます。
（ゾーン分離しない場合は子アカウントへのサブドメインの委譲は不要です。）

MyDNS.JPにLOGINしてDOMAIN INFO画面でホストレコードのTargetID=子アカウントで登録すると、そのレコードは子アカウントで通知したIPになります。

MyDNS.JPでサブドメインのゾーン分離を行うには、MyDNS.JPにLOGINしてUSER INFO画面で子アカウントの追加を行ってから、
MyDNS.JPにLOGINしてDOMAIN INFO画面で「Hostname=サブレベルドメイン名、Type=DELEGATE、TargetID=子アカウント」を設定することで、サブドメインを子アカウントに委譲できます。

親アカウントのドメインと子アカウントのサブドメインの両方の証明書を取得する場合は、親アカウントと子アカウントの両方の認証情報をMyDnsJpアカウント設定ファイルに記載してください。
```ini
[dns_mydnsjp_credential]
[[example.mydns.jp]]
'id'='mydns_jp_masterid'
'pwd'='mydns_jp_masterpassword'
[[sub.example.mydns.jp]]
'id'='mydns_jp_childid'
'pwd'='mydns_jp_childpassword'
…
```

MyDNS.JPはアカウント1つでドメイン1つ登録します。（複数のドメインをMyDNS.JP登録する場合は、複数のアカウント登録を行います。）
MyDnsJpアカウント設定ファイルに複数のドメインを記載すれば、MyDNS.JPを用いたマルチドメイン証明書の取得にも対応できます。
```ini
[dns_mydnsjp_credential]
[[example1.mydns.jp]]
'id'='mydns_jp_mastrid1'
'pwd'='mydns_jp_masterpassword1'
[[example2.mydns.jp]]
'id'='mydns_jp_masterid2'
'pwd'='mydns_jp_masterpassword2'
…
```

### certbotの実行
certbotのコマンドラインオプションに下記を加えることでMyDNS.JPでDNS-01 challengeを行います。（他のオプションはcertbotのページを確認してください。）
```commandline
certbot \
  --preferred-challenges dns \
  --authenticator dns-mydnsjp \
  --dns-mydnsjp-credentials <MyDnsJpアカウント設定ファイル(例:mydns.ini)>
  …
```

certbot実行中にエラーが発生した場合、認証後のDNS TXTレコードの削除／復元に失敗することがありますのでMyDNS.JPにLOGINしてDOMAIN INFO画面でレコード内容を削除／修正してください。

（DNS-01 challenge認証で使用するTXTレコードはhostnameが「_acme-challenge」で始まるTXTレコードです。）

### プラグインのコマンドラインオプション

| オプション | 機能・用途 |
|:---:|:---:|
| --dns-mydns-propagation-seconds <待機秒数> | DNS設定後の待ち時間（秒）デフォルト=30 |
| --dns-mydns-credentials <MyDNSアカウント設定ファイル名> | MyDnsJpアカウントを記載したファイル名を指定する |
| --dns-mydns-no-txt-restore | DNS-01 challenge認証後に使用したTXTエントリを削除する（このオプションを指定しない場合：使用したTXTエントリを元に戻す） |

## パッケージのビルド
パッケージのリビルドが必要な場合は、下記ビルド手順を参照してください。

### snapパッケージのビルド
[snapcraftをインストール](https://snapcraft.io/docs/create-a-new-snap)してから、下記を実行します。
```commandline
git clone https://github.com/usk-johnny-s/certbot_dns_mydnsjp
cd certbot_dns_mydnsjp
snapcraft
```

<details><summary>snapパッケージの公開</summary>

GUIデスクトップでkeyringを初期化
```commandline
gnome-keyring-daemon --unlock
```

SnapStoreのログイン情報をkeyringに登録
```commandline
snapcraft login
```

SnapStoreのWebでパッケージ名を申請（承認されてからパッケージを送信）

SnapStoreにパッケージを送信
```commandline
snapcraft login
snapcraft upload --release=stable certbot-dns-mydnsjp_*_amd64.snap
```
</details>

### Dockerイメージのビルド
[Dockerをインストール](https://docs.docker.com/get-docker/)してから、下記を実行します。
```commandline
git clone https://github.com/usk-johnny-s/certbot_dns_mydnsjp
cd certbot_dns_mydnsjp
docker build -t uskjohnnys/certbot-dns-mydnsjp:latest .
```

<details><summary>Dockerイメージの公開</summary>

DockerHubにログイン
```commandline
docker login
```

DockerHubにイメージを送信
```commandline
docker push uskjohnnys/certbot-dns-mydnsjp:latest
```
</details>

### Pythonパッケージのビルド
[setuptoolsをインストール](https://setuptools.pypa.io/en/latest/userguide/quickstart.html)してから、下記を実行します。
```commandline
git clone https://github.com/usk-johnny-s/certbot_dns_mydnsjp
cd certbot_dns_mydnsjp
python -m build
```

<details><summary>Pythonパッケージの公開</summary>

PyPIのログイン情報を~/.pypircに記入
```ini
[pypi]
  username = __token__
  password = ＜pypiログイントークン＞
```

PyPIにパッケージを送信
```commandline
python3 -m twine upload --repository pypi dist/*
```
</details>

## 謝辞

[*disco-v8/DirectEdit*](https://github.com/disco-v8/DirectEdit) MyDNS.JP純正のDNS認証用スクリプト。自分の用途「ゾーン分離しないサブドメイン＋マルチドメイン」には適合せず、このプラグインを開発する切っ掛けとなった。

[*infinityofspace/certbot_dns_duckdns*](https://github.com/infinityofspace/certbot_dns_duckdns) 非常にシンプルなcertbot用DNS認証プラグイン。このプラグインを開発する際にソースコードの骨格として参照した。
