$(function() {
    $('#btnSignUp').click(function() {
        console.log("Sign up JavaScript function");
        $.ajax({
            url: '/signUp',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response)
            {


                console.log('SUCCESS')
                console.log (response.status)
                console.log(response)
                var str1 = "/userHome/";
                var str2 = response;
                var str3 = "?source=1";
                var path = str1.concat(str2);
                var path = path.concat(str3);

                window.location = path;
            },
            error: function(error) {
                console.log(" Debug error in signUp.js");
                console.log (error);
                console.log(error.error);
                var str1 = "/showSignUp?error=";
                var str2 = "User or email already exist!";
                var path = str1.concat(str2);

                window.location = path;
            }
        });
    });
});
