$(document).ready(function () {
    // Init
    $('.loader').hide();
    $('#result').hide();

	
	// 基于准备好的dom，初始化echarts实例
    var myChart = echarts.init(document.getElementById('mainpad'));
	myChart.showLoading();
	
	// 加载图表的配置项，并显示图标
	$.getJSON("./static/js/twitter-prediction-chart-option.json",function (option,status) {
		if(status == 'success'){
        	myChart.hideLoading();
        	myChart.setOption(option);
		}
    });
	$('#mainpad').hide();
	


     // 开始测试
    $('#btn-predict').click(function () {
        var input_text =$('#input-text').val();
		if(input_text==""){
			alert("请输入要分析的微博文本！");
			return;
		}
		
        // Show loading animation
        $('#btn-predict').hide();
		$('#btn-random').hide();
        $('.loader').show();

        // 组装发送的json数据
		var sendjson = {
		  "type": "twitter",
		  "input_text": input_text
        };

        // Make prediction by calling api /predict
        $.ajax({
            type: 'POST',
            url: '/predict',
            data: JSON.stringify(sendjson),
            contentType: "application/json; charset=utf-8",
			dataType: "json",
            cache: false,
            processData: false,
            async: true,
            success: function (data) {
				console.info(data);
                // Get and display the result
                $('.loader').hide();
				$('#btn-predict').show();
				$('#btn-random').show();
				$('#actual_label').empty();
				$('#predicted_label').fadeIn(400);
                $('#predicted_label').text(' 预测情感: ' + data.predict );
				$("#print_sentence").empty();
				$('#print_sentence').fadeIn(800);
				$("#print_sentence").append(data.print_sentence);
				
				myChart.setOption({
					 series: [
					  {
						  name: "积极",
						  data: [parseInt(data.positive_percent*100)]
					  },
					  {
						  name: "消极",
						  data: [parseInt(100-data.positive_percent*100)]
					  }
				  ],
			     });
				$('#mainpad').show();
                console.log('Success!');
            },
        });
    });
	
	// 随便测测
	$('#btn-random').click(function () {
		
        // Show loading animation
        $('#btn-predict').hide();
		$('#btn-random').hide();
        $('.loader').show();

        // 组装发送的json数据
		var sendjson = {
		  "type": "twitter_random",
        };

        // Make prediction by calling api /predict
        $.ajax({
            type: 'POST',
            url: '/predict',
            data: JSON.stringify(sendjson),
            contentType: "application/json; charset=utf-8",
			dataType: "json",
            cache: false,
            processData: false,
            async: true,
            success: function (data) {
				console.info(data);
				$('#input-text').val(data.input_text);
                // Get and display the result
                $('.loader').hide();
				$('#btn-predict').show();
				$('#btn-random').show();
				
				
                $('#actual_label').fadeIn(400);
                $('#actual_label').text(' 实际情感:  ' + data.actual );
				
				$('#predicted_label').fadeIn(400);
                $('#predicted_label').text(' 预测情感: ' + data.predict );
				$("#print_sentence").empty();
				$('#print_sentence').fadeIn(800);
				$("#print_sentence").append(data.print_sentence);
				
				myChart.setOption({
					 series: [
					  {
						  name: "积极",
						  data: [parseInt(data.positive_percent*100)]
					  },
					  {
						  name: "消极",
						  data: [parseInt(100-data.positive_percent*100)]
					  }
				  ],
			     });
				$('#mainpad').show();
                console.log('Success!');
            },
        });
	});
	
	
});
