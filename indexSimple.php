<!DOCTYPE html>
<html>

<head>
    <meta charset="utf-8">
    <title>hackPi</title>
    <!-- JavaScript to handle RaspPi Buttons -->
    <script src="http://code.jquery.com/jquery-1.11.0.min.js"></script>
    <script type="text/javascript">
        $(document).ready(function(){
            $('#clickON').click(function(){
                var a = new XMLHttpRequest();
                a.open("GET","pinon.php");
                a.onreadystatechange=function(){
                    if(a.readyState==4){
                        if(a.status == 200){
                        }
                        else alert("HTTP ERROR");
                    }
                }
                a.send();
            });

            $('#clickOFF').click(function(){
                var a = new XMLHttpRequest();
                a.open("GET","pinoff.php");
                a.onreadystatechange=function(){
                    if(a.readyState==4){
                        if(a.status == 200){
                        }
                        else alert("HTTP ERROR");
                    }
                }
                a.send();
            });
        });
    </script>

</head>

<body>
    <button type="button" id="clickON">On</button>
    <button type="button" id="clickOFF">Off</button>
</body>

</html>
