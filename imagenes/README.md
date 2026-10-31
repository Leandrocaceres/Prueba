# Referencias visuales originales

Esta carpeta contiene las imágenes originales del usuario, sin regenerarlas ni
alterar su encuadre. La aplicación las muestra completas, con proporciones
conservadas, y permite abrir el original desde la ficha.

`referencias.json` asocia las imágenes por nombre exacto del personaje o título
de la entrada del mundo. Las referencias principales de Fumi, Horo y Enzi ya están incorporadas:

```json
{
  "personajes": {
    "Fumi": {"archivo": "fumi.jpg", "alt": "Retrato de Fumi"},
    "Horo": {"archivo": "horo.png", "alt": "Retrato de Horo"},
    "Enzi": {"archivo": "enzi.png", "alt": "Retrato de Enzi"}
  },
  "mundo": {}
}
```

Conserva el resto de las asociaciones al añadir nuevas referencias. Se admiten
PNG, JPG, JPEG y WebP. Guarda el archivo directamente en esta carpeta y usa su
nombre simple, sin rutas. Las imágenes y el catálogo forman parte del proyecto;
no dependen de las rutas temporales de los adjuntos del chat.

El archivo `fumi.jpg` es el original `rML71ub.jpg` recibido dentro de `Fumi.zip`.
Se conservan exactamente sus bytes y su resolución de 512 × 512 píxeles. Es el
retrato principal de Fumi y se muestra al abrir su ficha, sin recortar ni regenerar.
SHA-256: `908bfeee1c0bbc2c7504512bc6da6600d14a412db094365796f09089815aa16d`.

El archivo `horo.png` es el original `Horo.png` recibido dentro de `Horo.zip`.
Se conservan exactamente sus bytes y su resolución de 1280 × 720 píxeles. Es el
retrato principal de Horo y se muestra completo, sin recortar ni regenerar.
SHA-256: `431a24f71436aade6cde54ee66c36a4182af9223a218dadec899aadc871f6550`.

El archivo `enzi.png` es el original `7a10464e-3bef-4f24-a128-c3c49076f95b.png`
recibido dentro de `Enzi.zip`. Se conservan exactamente sus bytes y su resolución
de 1086 × 1448 píxeles. Es el retrato principal de Enzi; no se recorta ni regenera.
SHA-256: `a9d747ac994e082a945c204c03f089c9bf5e8125ab9b9b4f30c2c4fcbb198665`.
La regla de exactamente tres colas sigue vigente para las nuevas ilustraciones;
la incorporación de esta referencia no modifica el canon escrito.

Al cambiar de nombre un personaje o una entrada del mundo, actualiza también
su clave en este catálogo. La exportación JSON de campaña incluye las rutas
de las imágenes disponibles; para respaldar sus archivos copia esta carpeta.

## Retratos por identidad

La ficha de Enzi incluye un selector de identidades. En `referencias.json`,
`archivo` de Enzi conserva su retrato principal y `identidades` permite añadir
los retratos de Enmy y Víctor:

```json
"Enzi": {
  "archivo": "enzi.png",
  "identidades": {
    "Enmy": {"archivo": "enmy.png", "alt": "Retrato de Enmy"},
    "Víctor": {"archivo": "victor.png", "alt": "Retrato de Víctor"}
  }
}
```

Los retratos de Enzi, Enmy y Víctor están disponibles en el selector.
Todas las imágenes son los originales proporcionados por el usuario. Los nombres del selector proceden
del campo `identidades` de la ficha, separados por punto y coma. La ficha,
las relaciones y el recuento de personajes siguen siendo los de Enzi.

El archivo `enmy.png` es el original `5c3a2084-aaa7-4d36-ad3d-dadb0324f1c0.png`
recibido dentro de `Enmy.zip`. Se conservan exactamente sus bytes y su resolución
de 1086 × 1448 píxeles, sin recortar ni regenerar. Se muestra en la ficha de Enzi
al seleccionar Enmy; no añade otra persona al recuento de residentes.
SHA-256: `2bc3d1fc75f6a1980075ce5544d22ad0549bb766cb71be9da624a75372dd44ce`.

## Asuka

El archivo `asuka.png` es el original `ce45bfadd7c40f32081975abe7bd63d0.png`
recibido dentro de `Asuka.zip`. Conserva sus bytes y resolución de 334 × 472
píxeles. Es el retrato principal de Asuka y se muestra completo en su ficha,
sin recortarlo ni regenerarlo.
SHA-256: `85158ca81fa4e6c4273a06d76269d77cfa8dda6797e6b12f0d0c6505048bde94`.

## Hikari

El archivo `hikari.png` es el original `sample-3f573b81dc66864d1c98fdb1aa4830cd.png`
recibido dentro de `Hikari.zip`. Conserva sus bytes y resolución de 526 × 473
píxeles. Es el retrato principal de Hikari y se muestra completo en su ficha,
sin recortarlo ni regenerarlo.
SHA-256: `86c0f4c32aaf6d4dcd2896e51a92ef38417da96757ac13f1e64fe380b79519d8`.

## IA

El archivo `ia.jpg` es el original `Assassin.Katou.Danzou.600.2280249.jpg`
recibido dentro de `IA.zip`. Conserva sus bytes y resolución de 424 × 600
píxeles. Está asociado a IA, la sirvienta salomónica del caserón, según la
identificación del usuario; el nombre del archivo no altera su identidad.
Se muestra completo en su ficha, sin recortarlo ni regenerarlo.
SHA-256: `18cda8c1556baef4511a8734f657504298b26ee90912af21dc9704a51c6d9558`.

## Yuna

El archivo `yuna.jpg` es el original `687097639f8da9986e6d55192050166b-1.jpg`
recibido dentro de `Yuna.zip`. Conserva sus bytes y resolución de 500 × 527
píxeles. Es el retrato principal de Yuna y se muestra completo en su ficha,
sin recortarlo ni regenerarlo. Sus orejas y cola son accesorios, según el canon;
la referencia no altera esa condición ni su vínculo romántico parcial con Enzi.
SHA-256: `c5fa4ae6ec98c42c197391495b120b6555e4b7f790022e6c1065cbaa465c7ee9`.

## Tamamo Aria · ficha de Aria

La referencia identificada por el usuario como Tamamo Aria se vincula a la ficha
existente de Aria, sin duplicarla ni modificar sus relaciones o su trasfondo.
El archivo `aria.webp` es el original `Tamamo_Aria_SR.webp` recibido dentro de
`Tamamo_Aria.zip`. Conserva sus bytes, transparencia y resolución de 886 × 1010
píxeles. Se muestra completo, sin recortarlo, regenerarlo ni convertirlo.
También se encuentra buscando «Tamamo Aria» a través del texto de la referencia.
SHA-256: `5f574fcd7e49df4c9c97fd507fd50a9820ba76ebf29afcfabb485f3139ad9bab`.

## Pip

El archivo `pip.png` es el original `unknown-14.png` recibido dentro de `Pip.zip`.
Conserva sus bytes y resolución de 850 × 1159 píxeles. Es el retrato principal
de Pip en forma humana y se muestra completo, sin recortarlo ni regenerarlo.
La referencia no modifica la maldición: cada beso alterna su forma y Pip no
puede transformarse voluntariamente.
SHA-256: `a346e03ffa0ede5dbac305ae982616973bbd47023c7009c2bfc9fa637c7ec1d5`.

## Shiey

El archivo `shiey.png` es el original `Shiey.png` recibido dentro de `Shiey.zip`.
Conserva sus bytes y resolución de 1024 × 1024 píxeles. Es el retrato principal
de Shiey y se muestra completo en su ficha, sin recortarlo ni regenerarlo.
SHA-256: `98a7a9b4dca193af8a1e826425be6b0b656add43d6e096cd96b5e99528da8d8f`.

## Mary y Mimy · imagen compartida

El archivo `mary-mimy.png` es el original `GVFo7FdaEAAJNaJ.png`, recibido dentro
de `Mary y mimy.zip`. Conserva sus bytes y resolución de 1000 × 1000 píxeles.
Por petición del usuario, ambas fichas utilizan este mismo archivo; no se duplica,
recorta ni regenera la imagen. Mary y Mimy conservan sus propias fichas, nombres,
historias y relaciones. No se fusionan en un único personaje.
SHA-256: `dc7b5b9bfe078edf6d43fac6dfc56e5092eeecc42e154d8f7c9ba336beaea97a`.

## Lerey

El archivo `lerey.png` es el original `Lerey.png` recibido dentro de `Lerey.zip`.
Conserva sus bytes y resolución de 2048 × 2064 píxeles. Es el retrato principal
de Lerey y se muestra completo en su ficha, sin recortarlo ni regenerarlo.
La referencia no modifica su historia ni sus conocimientos sobre Víctor.
SHA-256: `494daf6af0399ce8368a994523df506775ebd9825bc7c5e4d5fc3d825780c3cd`.

## Sery Factar

El archivo `sery-factar.jpg` es el original `Sery Factar.jpg` recibido dentro de
`Sery Factar.zip`. Conserva sus bytes y resolución de 735 × 1040 píxeles.
Es el retrato principal de Sery Factar y se muestra completo en su ficha,
sin recortarlo ni regenerarlo. No modifica su historia ni la confunde con el
inquisidor incidental de la antigua misión de Enzi y Horo.
SHA-256: `7be10ef97db321414180fee4ed5b8ec0848e2e3bcf9d5b24d4d931e2501a1722`.

## Benienma-Sama

El archivo `benienma-sama.png` es el original `Beni-sama.png` recibido dentro de
`Benienma-Sama.zip`. Conserva sus bytes y resolución de 512 × 724 píxeles.
Es el retrato principal de Benienma-Sama y se muestra completo en su ficha,
sin recortarlo ni regenerarlo. Su historia y su vínculo con Aria se conservan.
SHA-256: `9f61473933d5e235b9bb62a629273022400be8ef96dc54853e44cfe582f1b298`.

## Jazmín

El archivo `jazmin.png` es el original `Jazmin.png` recibido dentro de `Jazmin.zip`.
Conserva sus bytes y resolución de 540 × 960 píxeles. Es el retrato principal
de Jazmín y se muestra completo en su ficha, sin recortarlo ni regenerarlo.
Su ocupación y su historia se conservan sin añadir hechos a partir del fondo
u otros elementos de la ilustración.
SHA-256: `d32e7c634fce8d71feb046614f571bba679fdf502ec58f1df5ab67ae59aee3f6`.

## Eiko

El archivo `eiko.png` es el original `Eiko.png` recibido dentro de `Eiko.zip`.
Conserva sus bytes y resolución de 735 × 1137 píxeles. Es el retrato principal
de Eiko y se muestra completo en su ficha, sin recortarlo ni regenerarlo.
La referencia no modifica su relación profesional con Fumi ni su desconocimiento
de la naturaleza feérica de su socia.
SHA-256: `de8b59970994ac2692258a0a6c63597fab496f8d2ff14146e27f47629ae119ff`.

## Exusiai

El archivo `exusiai.jpg` es el original `images.jpg` recibido dentro de `Exusiai.zip`.
Conserva sus bytes y resolución de 367 × 544 píxeles. Es el retrato principal
de Exusiai y se muestra completo en su ficha, sin recortarlo ni regenerarlo.
La referencia no añade habilidades o acontecimientos a su historia ni cambia
su relación con Lappland o el secreto de su pertenencia a Samael.
SHA-256: `ac0b9df645fd92bd0c195f69a6866bdb2cad065dfa8c8a591c5cfe3a3a0f6a7c`.

## Lappland

El archivo `lappland.png` es el original `HSltH1oakAAcd2m.png`, recibido dentro de
`Lappland.zip`. Conserva sus bytes y resolución de 2704 × 4096 píxeles. Es la
referencia principal de Lappland y se muestra completa en su ficha, sin recortarla
ni regenerarla. Las distintas representaciones dentro de la ilustración no
crean nuevos personajes ni identidades. Se conservan su historia y relaciones.
SHA-256: `9d5791c3a0d4b38a00a4ca239042ef690292775b5c22f21c4b29215e13abea6c`.

## Salama

El archivo `salama.jpg` es el original `B1H7OAOIQAAKA5j.jpg_large.jpg`, recibido
dentro de `Salama.zip`. Conserva sus bytes y resolución de 1440 × 1724 píxeles.
Es el retrato principal de Salama y se muestra completo en su ficha, sin recortarlo
ni regenerarlo. No se infieren habilidades ni acontecimientos a partir de la
ilustración. Se conservan los secretos y vínculos establecidos en el canon.
SHA-256: `0cede1b14fb22d9db432dcfcef591739f591fc7d8e8060c67110be22d2f2a887`.

## Víctor · identidad de Enzi

El archivo `victor.png` es el original `Voctor.png`, recibido dentro de
`Victor.zip`. Conserva sus bytes y resolución de 1199 × 1312 píxeles.
Se muestra completo al seleccionar Víctor en la ficha de Enzi, sin recortarlo
ni regenerarlo. No crea otro personaje ni modifica los secretos establecidos.
SHA-256: `4b7b731e786c82871ff9482c3234a7754f2e1094fcd8ad01751259ba0abb081e`.
