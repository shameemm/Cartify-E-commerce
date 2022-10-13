$(document).ready(function() {
    $('.payWithRazorpay').click(function (e) { 
        e.preventDefault();

        $.ajax({
            type: "GET",
            url: "/razorpay",
            success: function (response) {
                console.log(response);
                
            }
        });
        var options={
             
        }
        var rzp1 = new Razorpay(options);
        rzp1.open();
        
    });
});