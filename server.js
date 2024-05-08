const express = require('express');
const bodyParser = require('body-parser');
const app = express();
app.use(bodyParser.json());

app.post('/basvuru', (req, res) => {
    console.log('Başvuru alındı:', req.body);
    // Burada başvuruyu veritabanına kaydedebilirsiniz veya başka işlemler yapabilirsiniz.
    res.send({ url: 'http://localhost:3000/giris' });
});

app.listen(3000, () => {
    console.log('Sunucu http://localhost:3000 adresinde çalışıyor.');
});
