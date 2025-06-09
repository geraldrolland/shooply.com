const emailVerificationTemplate = (verification_link) => {
    return `<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="https://fonts.googleapis.com/css2?family=Roboto&family=Oswald&family=Imprima&display=swap" rel="stylesheet">
    <title>Document</title>
    <style>
        * {
            padding: 0;
            margin: 0;
            box-sizing: border-box;
        }
    </style>
</head>
<body style="width: 100%; height: 100%; background-color: #0B1D51; padding: 15px; font-size: 18px;">
    <p style="text-align: justify; color: #D1C6AD; font-family: Oswald, sans-serif;">Thank you for signing up! To complete your registration and start using your account, please verify your email address.</p>
    <h1 style="color: #797596; font-size: 20px; margin-top: 20px;">To verify your email, simply click the button below:</h1>
    <a href="${verification_link}" style=" color: white; width: 200px; height: 50px; border: 1px solid black; background-color: #A1869E; border: none; border-radius: 5px; margin: auto; display: block; margin-top: 30px; text-decoration: none; color: white; font-weight: bold;">Verify Email Address</a>
</body>
</html>`
}

module.exports = {
    emailVerificationTemplate,
}