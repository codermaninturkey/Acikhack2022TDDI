PYTHON-OCR-SERVICE

Servis, FastAPI web çerçevesi üzerine inşa edilmiştir. FastAPI, standart Python türü ipuçlarına dayalı Python 3.6+ ile API'ler oluşturmaya yönelik modern, hızlı (yüksek performanslı) bir web çerçevesidir. Kurulumu ve kullanımı basit, hızlı, kolay kodlama, esnek, neredeyse Go ve NodeJS ile aynı şekilde yüksek performans  (Starlette/hafif, hızlı http web çerçevesi ve Pydantic/veri doğrulama, ayarlama, modelleme/ sayesinde) sunabilmektedir. Python için en hızlı çerçevelerden biridir. Bu sebeble tercih edilmiştir.

FastAPI Kurulum:
pip install fastapi

Web Server
Web sunucusu için local testler de uvicorn kullanılsada prod ortamında yetersiz kalması sebebiyle gunicorn kullanılmıştır. Bu sebeble kullanım için ikisininde sistem olması iyi olacaktır. BEnim tavsiyem gunicorn üzerindne kullanım yapmanız olacaktır, bu yazının devamında da gunicorn üzerinden devam edilecektir. Çünkü gunicorn, Instagram gibi dünyanın en büyük Python destekli web uygulamalarından bazılarını destekleyen web uygulaması dağıtımlarının yaygın olarak kullanılan bir parçasıdır .

**pip install "uvicorn[standard]"  #kütüphaneyi bağımlıkları ile yükler
pip install gunicorn** #sadece hütüphane yükler, bağımlılıkları kontrol etmez

Artık sistemimiz hazır. Şimdi artık diğer tanımlamalar ve dosya yapısını tanıma ile ilgilenebiliriz.

requirements.txt: 	bağımlılıklar

API KLASÖRÜ :

main.py:	  web çerçevisinin ilgili ayarlarının ve route işlemlerinin yapıldığı bölüm

ocrservice.py:     bütün işlemlerin yapıldı bölüm, burayı detaylı şekilde açıklayalım.

Ocr işlemleri için servisi hizmeti sağlayan bölüm. Burada iki adet endpoint noktası ile işlem yapılır. Post işlemlerinde çalışır.

/multipart:     file olarak gelen image nesneleri için ocr işlemleri yapan endpint noktası. 4 adet parametre alır.
file: image file
**pageNumbers: **özellikle tiff belgeleri ve pdf belgeleri için hangi sayfaların ocr edilmesi istenildiğini tutar. Defalt olarak "o" dır. 0 olması durumunda tüm sayfayı işleme alır. Eğer ki 2,4,6 olarak verilir sadece bu sayfaları ocr ederek sonuç döndürür.
stats: bu değişken ocr işlemi sonra confidence değeri dönüp dönmeyeceğini belirten boolean türünde bir veridir. Default olarak false dir.
deep: ocr işleminin derinliğidir. işlemin derinliği ve yüzeyselliğini belirtir. Gürültü belgeler için true seçilmesi önerilir, default olarak false değerini alır.

/byte-array:byte olarak gelen image verileri için ocr işlemleri yapan endpint noktası. 4 adet parametre alır.. file protokollerini devre dışı bıraktığı için biraz dha hızlı çalıştığı söylenebilir.
Post Body Json yapısı şu şekildedir:
**Request Model Schema:
{
"applicationName": "appname",
"data": {
"content": "byte-image-string",
"stats": false,
"deep": false,
"page": ""
}
}**

parametre açıklamaları ise /multipart ile aynı olmakla beraber şu şekildedir:
file: image file
pageNumbers: özellikle tiff belgeleri ve pdf belgeleri için hangi sayfaların ocr edilmesi istenildiğini tutar. Defalt olarak "o" dır. 0 olması durumunda tüm sayfayı işleme alır. Eğer ki 2,4,6 olarak verilir sadece bu sayfaları ocr ederek sonuç döndürür.
**stats: **bu değişken ocr işlemi sonra confidence değeri dönüp dönmeyeceğini belirten boolean türünde bir veridir. Default olarak false dir.
**deep: **ocr işleminin derinliğidir. işlemin derinliği ve yüzeyselliğini belirtir. Gürültü belgeler için true seçilmesi önerilir, default olarak false değerini alır.
**Response Model Schema:
{
"data": {
"filename": null,
"ocrResponses": [
{
"text": "Sana gitme demeyeceğim\nÜşüyorsun ceketimi al\n\nGünün en güzel saatleri bunlar\nYanımda kal\n\nSana gitme demeyeceğim\nGene de sen bilirsin\nYalanlar istiyorsan, yalanlar söyleyeyim",
"pageNumber": null,
"confidence": null
}
]
},
"detailMessage": "",
"status": "SUCCESS"
}**

Şimdi servisi ayağa kaldırıp, swagger-ui arayüzü ile ve postman üzerinden test edebiliriz.
ayağa kaldırmak işin:
gunicorn api.main:app --bind "0.0.0.0:8017" --workers 2 --worker-class uvicorn.workers.UvicornWorker --timeout 60
swagger-ui arayüzü için:
http://localhost:8017/docs


Tesseract Kurulum
Bu uygulama, python ortamında tesseract kütüphanesi kullanılarak ocr işlemlerini gerçekleştirmek amacıyla geliştirilmiştir. Uygulama web servis olarak çalışacak şekilde geliştirilmiştir. Sistemin temel bileşeni olan "Tesseract" kütüphanesi ve web sunucusu olarak kullanılan "Flask" hakkında bilgiler aşağıda belitilmiştir.

Tesseract, açık kaynak kodlu bir optik karakter tanıma motorudur ve gerek kurulumu gerek kullanımı ve gerekse başarısı ile çok geniş kitlelere yayılabilmiştir. Tesseract belge üzerinde ki metinleri arama işlemini yaparken makine öğrenmesi algoritmalarını kullanır. Belge üzerinde harf, kelime ve cümleler için çeşitli şablonları vardır ve bu sayede daha az kayıpla metin tanımlaması yapabilmektedir.

Tesseract'ın cıkış amacı faturaları tanımak olsada daha çok belge üzerinde ki kelimeleri tanımak ve anlamlı şekilde bir dönüştürmek amacıyla kullanılabilmektedir. Detaylı araştırmalarla çok farklı kullanım alanları geliştirilebilir. C++ üzerine yazıldığı için üçüncü parti bir sarıcı aracılığıyla python başta olmak üzere çok farklı geliştirme ortamlarında sorunsuzca kullanılabilmektedir. Farklı kullanım alanlarına göre eğitilmiş modelleri kullanır. "tessdata" klasörü altında [best, standart, fast olarak üç farklı model bulunur. Bunların her birinin farklı amaçları vardır. Metin üzerinde ki ocr kalitesi artarken işlem süresi uzamakta veya ocr kalitesi azaltılırken işlem süre kısaltılabilmektedir; bu durum tamamen kullanım amacınıza göre değişiklik göstermektedir.

Her dil için her dosya için metin tanıma için veri içeren dosyaya ihtiyacımız var. Türkçe desteğini ve başarısını buradan belirtmekde fayda var. Dil dosyaları için https://github.com/tesseract-ocr/langdata adresini kontrol edebilirsiniz.

Tesseract ile genel bilgileri verdikten sonra Ubuntu 16.04 üzerinde paketi kuralım. Burada Tesseract'ın en son kararlı sürümü olan Tesseract 4.1.1 sürümünü yükleyeceğiz. Tesseract 4.1.1'i kurmaya başlamadan önce, birkaç bağımlılık yüklememiz gerekiyor. İlk olarak görüntü işleme ve görüntü analizi uygulamaları için geniş ölçüde yararlı olan yazılımları içeren bir açık kaynak kitaplığı olan "leptonica" kitaplığını kurmamız gerekiyor . http://www.leptonica.org/

Teseract'ın gerektirdiği tüm bağımlıkları https://github.com/tesseract-ocr/tesseract/blob/master/INSTALL.GIT.md adresinden kontrol edebilirsiniz. O halde başlayalım.

$ sudo apt-get install -y libleptonica-dev

Şimdi sırasıyla diğer bağımlıkları da yükleyelim. Eğer ki sisteminiz içerisinde mevcutsa bu adımları atlayabilirsiniz.

$ sudo apt-get update -y 
$ sudo apt-get install automake 
$ sudo apt-get install -y pkg-config 
$ sudo apt-get install -y libsdl-pango-dev 
$ sudo apt-get install -y libicu-dev 
$ sudo apt-get install -y libcairo2-dev 
$ sudo apt-get install bc

Bağımlılıkları yükledikten sonra https://github.com/tesseract-ocr/tesseract adresine giderek teseractın kararlı son sürümünü öğrenebilirsiniz. Bu çalışma yapıldığı sırada kararlı sürüm 5.2.0 dı. Fakat Ubuntu 16.4 üzerine 4.1.1 sürümünü kuracaktır.

sudo apt install tesseract-ocr

Bunun yanısıra eğitim için kullanılabilecek geliştirici araçlarını kurmak istiyorsanız , şu komutu çalıçalıştırmanız yeterli olacaktır:

**sudo apt install libtesseract-dev **

Diğer bir kurulum ise manul yöntemlerdir. O da şu şekilde olmaktadır :

Öncelikle dosyayı indiriyoruz. $ wget https://github.com/tesseract-ocr/tesseract/archive/4.1.1.zip

Daha sonra zip dosyası açıyoruz. $ unzip 4.1.1.zip

Sonra dizin içerisine giriyoruz $ cd tesseract-4.1.1

Artık kurulumu y apmaya hazırız. Şimdi şu komutları sırasıyla çalıştıralım:

$ ./autogen.sh 
$ ./configure 
$ make 
$ sudo make install 
$ sudo ldconfig 
$ make training 
$ sudo make training-install

Tesseract version kontrolü için şu komutu kullanabilirsiniz: 
$ tesseract --version

Sonuç olarak herşey yolunda gitti ise şu şekilde bir sonuç almalısınız: 
**tesseract 4.1.1 leptonica-1.75.3 libgif 5.1.4 : libjpeg 8d (libjpeg-turbo 1.5.2) : libpng 1.6.34 : libtiff 4.0.9 : zlib 1.2.11 : libwebp 0.6.1 : libopenjp2 2.3.0

Found AVX2 Found AVX Found FMA Found SSE**

Şimdi sıra "tessdata" klasörünü yapılandırmada. Tessdata, tesseract'ın giriş belgesinde OCR gerçekleştirmek için ihtiyaç duyduğu dil verilerini kontrol ettiği yerdir. Sistem environmment tanımlamasını yaparak kulanabiliriz. Ama öncelikle sisteme tessdata kalasörünü indirmeniz gerekecek. Adımlar şu şekildedir: Bu adreste https://tesseract-ocr.github.io/tessdoc/Data-Files.html tesseracta ait [standart, fast, best] dil dosyaları mevcut. Bunları tessdata klasörü altına alıyoruz, ve daha sonra sistem environment tanımlamalarını yapıyoruz:

TESSDATA_PREFIX=/usr/local/share/tessdata

klasör içerisine hangidil paketini kullanmak istiyorsanız sadece onu koymalısınız, çünkü isimlendirme hepsinde aynı, klasörden otomatik olarak çekme işlemini tesseract yapıyor. Bu işlemler tamamlandıktan sonra

**tesseract --list-langs **

komutunu çalıştırarak yüklü olan dil dosyalarını görüntüleyebiliriz. Bende ekranda çıktı bu şekilde olmaktadır, bu ekran sisde farklılıklar gösterebilir.

List of available languages (8): 
best/eng best/tur eng fast/eng fast/tur standart/eng standart/tur tur
