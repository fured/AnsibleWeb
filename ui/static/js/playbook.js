var playbookEvents = {
    'click #ymldetail': function (e, value, row, index){
         $.ajax({
             url: "/playbook/getdata/ymldetail",
             type: "POST",
             contentType: "application/json;charset=utf-8",
             data: JSON.stringify({"playbook_id": row.playbook_id}),
             dataType: "json",
             success: function(response){
                 if (response.code != 0){
                     alert("获取文件详情失败！"+ response.message)
                 }else{
                     content_yml = response.data.content;
                     $('#playbookcontent').modal();
                     $('#ymlcontent').empty();
                     $('#ymlcontent').append(content_yml);
                 }
             },
             error: function(){
                 alert("server error!")
             }
         })
    }
};

function toplaybook(){
$('#register_playbook').bootstrapTable({
    url: 'playbook/getdata/all',
    method: 'post',
    contentType: 'application/json',
    sidePagination: "server",
    pagination: true,
    showRefresh: true,
    search: true,
    uniqueId: "playbook_id",
    pageSize : 10,
    pageList : [ 10, 25, 50, 100, 'all' ],
    sortable: false,
    columns: [{
        field: "playbook_id",
        title: "剧本ID",
        align: "center",
        width: "6",
        widthUnit: '%'
    }, {
        field: "project_type",
        title: "项目类型",
        align: "left",
        width: "10",
        widthUnit: '%'
    }, {
        field: "project_name",
        title: "项目名称",
        align: "left",
        width: "15",
        widthUnit: '%'
    }, {
        field: "file_name",
        title: "剧本名称",
        align: "left",
        width: "15",
        widthUnit: '%'
    }, {
        field: "playbook_impact",
        title: "作用",
        align: "left",
        width: "15",
        widthUnit: '%'
    }, {
        field: "author",
        title: "作者",
        align: "left",
        width: "10",
        widthUnit: '%'
    }, {
        field: "register_time",
        title: "注册时间",
        align: "center",
        width: "20",
        widthUnit: '%'
    }, {
        field: "yml_oper",
        title: "操作",
        align: "center",
        width: "10",
        widthUnit: '%',
        events: playbookEvents,
        formatter: addPlaybookOper
    }]
})
};


// 生成操作按钮
function addPlaybookOper(value, row, index){
    return ['<button id="ymldetail" type="button" class="btn btn-default btn-info">详情</button>']
}


// 注册yml文件
$('#register_yml_file').click(function(){
    $('#registerymlmodal').modal();
});


//提交注册yml 文件
$('#commit_registeryml').click(function(){
    var p_file_name = $("#playbook_name").val();
    var p_project_type = $("#playbook_project_type").val();
    var p_project_name = $("#playbook_project_name").val();
    var p_impact = $("#playbook_impact").val();
    var p_author = $("#playbook_author").val();

    if (p_file_name == "" || p_project_name == "" || p_impact == "" || p_author == ""){
        alert("不允许有字段为空！");
        return;
    };

    var playbook = {
        "file_name": p_file_name,
        "project_name": p_project_name,
        "project_type": p_project_type,
        "playbook_impact": p_impact,
        "author": p_author
    };

    $.ajax({
        url: "/playbook/yml/register",
        type: "POST",
        contentType: "application/json;charset=utf-8",
        data: JSON.stringify(playbook),
        dataType: "json",
        success: function(response){
            if (response.code != 0){
                alert("注册失败！" + response.message);
            }else{
                alert("注册成功！");
                $('#registerymlmodal').modal('hide');
            }
        },
        error: function(){
            alert("server error")
        }
    })
});

