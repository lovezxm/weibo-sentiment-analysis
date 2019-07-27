$(document).ready(function () {
    // Init
    $('.loader').hide();
    $('#result').hide();
	// 改变 mainpaid 高度
	$('#mainpad').css("height","500px");
	
	// 基于准备好的dom，初始化echarts实例
    var myChart = echarts.init(document.getElementById('mainpad'));
	myChart.showLoading();
	
	// 加载图表的配置项，并显示图标
	$.getJSON("./static/js/weibo-hierarchical-chart-option.json",function (option,status) {
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
		  "type": "weibo",
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
				$('#predicted_label').fadeIn(800);
                $('#predicted_label').text("预测情感： " + data.pred_L1 +'  '+ data.pred_L2 + '  ' + data.pred_L3 );
				$("#print_sentence").empty();
				$('#print_sentence').fadeIn(400);
				$("#print_sentence").append("预处理结果： "+data.print_sentence);
				
				myChart.setOption({
					 series: [
					  {
						  name: "主客观情感分类",
						  data:  [{ value:parseInt(100-data.subject_percent*100), name: "客观"},
                                  { value:parseInt(data.subject_percent*100), name: "主观"}]
					  }
				     ],
			    });
				// 设置第二层分类结果
				if(data.pred_L1 == "主观"){
					myChart.setOption({
					series: [
					  {
						  name: "情感倾向性分类",
						  data:  [{ value:parseInt(100-data.positive_percent*100), name: "消极"},
                                  { value:parseInt(data.positive_percent*100), name: "积极"}]
					  }
				     ],
			    	});
				}else{// 如果是客观，就清空里面两层数据
					myChart.setOption({
					  series: [
						{
							name: "细粒度分类",
							data:  []
						},
						{
						  name: "情感倾向性分类",
						  data:  []
					    }
					   ],
			    	});
				}
				
				// 设置第三层分类结果
				if(data.pred_L2 == "积极"){
					myChart.setOption({
					series: [
					  {
						  name: "细粒度分类",
						  data:  [{ value:parseInt(100-data.like_precent*100), name: "高兴"},
                                  { value:parseInt(data.like_precent*100), name: "喜欢"}]
					  }
				     ],
			    	});
				}else if(data.pred_L2 == "消极"){
					myChart.setOption({
					series: [
					  {
						  name: "细粒度分类",
						  data:  [{ value:parseInt(data.negative_precent_list[0]*100), name: "害怕"},
						          { value:parseInt(data.negative_precent_list[1]*100), name: "生气"},
								  { value:parseInt(data.negative_precent_list[2]*100), name: "伤心"},
								  { value:parseInt(data.negative_precent_list[3]*100), name: "厌恶"},
                                  { value:parseInt(data.negative_precent_list[4]*100), name: "吃惊"}]
					  }
				     ],
			    	});
				}
				
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
		$("#print_sentence").empty();
		$("#actual_label").empty();
		$("#predicted_label").empty();
        $('.loader').show();

        // 组装发送的json数据
		var sendjson = {
		  "type": "weibo_random",
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
				
				$('#actual_label').fadeIn(600);
                $('#actual_label').text("实际情感： " + data.actual );
				
				$('#predicted_label').fadeIn(800);
                $('#predicted_label').text("预测情感： " + data.pred_L1 +'  '+ data.pred_L2 + '  ' + data.pred_L3 );
				
				$('#print_sentence').fadeIn(400);
				$("#print_sentence").append("预处理结果： "+data.print_sentence);
				
				myChart.setOption({
					 series: [
					  {
						  name: "主客观情感分类",
						  data:  [{ value:parseInt(100-data.subject_percent*100), name: "客观"},
                                  { value:parseInt(data.subject_percent*100), name: "主观"}]
					  }
				     ],
			    });
				// 设置第二层分类结果
				if(data.pred_L1 == "主观"){
					myChart.setOption({
					series: [
					  {
						  name: "情感倾向性分类",
						  data:  [{ value:parseInt(100-data.positive_percent*100), name: "消极"},
                                  { value:parseInt(data.positive_percent*100), name: "积极"}]
					  }
				     ],
			    	});
				}else{// 如果是客观，就清空里面两层数据
					myChart.setOption({
					  series: [
						{
							name: "细粒度分类",
							data:  []
						},
						{
						  name: "情感倾向性分类",
						  data:  []
					    }
					   ],
			    	});
				}
				
				// 设置第三层分类结果
				if(data.pred_L2 == "积极"){
					myChart.setOption({
					series: [
					  {
						  name: "细粒度分类",
						  data:  [{ value:parseInt(100-data.like_precent*100), name: "高兴"},
                                  { value:parseInt(data.like_precent*100), name: "喜欢"}]
					  }
				     ],
			    	});
				}else if(data.pred_L2 == "消极"){
					myChart.setOption({
					series: [
					  {
						  name: "细粒度分类",
						  data:  [{ value:parseInt(data.negative_precent_list[0]*100), name: "害怕"},
						          { value:parseInt(data.negative_precent_list[1]*100), name: "生气"},
								  { value:parseInt(data.negative_precent_list[2]*100), name: "伤心"},
								  { value:parseInt(data.negative_precent_list[3]*100), name: "厌恶"},
                                  { value:parseInt(data.negative_precent_list[4]*100), name: "吃惊"}]
					  }
				     ],
			    	});
				}
				
				$('#mainpad').show();
                console.log('Success!');
            },
        });
	});
	
	
});
