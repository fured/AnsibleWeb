// 注册父表操作事件
var groupEvents = {
    'click #deleteGroup': function (e, value, row, index){
        console.log("delete"+row.group_id);
        $('#confirmmodal').modal();
        var deletegroup_b = document.getElementById('confirm_button');
        deletegroup_b.onclick = function(){
            deletegroup(row.group_type, row.group_id);
        };
        if (row.group_type == "children"){
            document.getElementById('confirm_info').innerText = "删除子主机组将同时删除子主机组下的所有主机！"
        };
        if (row.group_type == "parent"){ 
            document.getElementById('confirm_info').innerText = "删除父主机组不会删除子主机组及子主机组下的所有主机！"
        }
    }
};

// 初始化主机表
function toinventory(){
    $('#hosts_group_table').bootstrapTable({
        url: '/inventory/getdata/allgroup',
        method: 'post',
        contentType: 'application/json',
        sidePagination: 'server',
        pagination: true,
        showRefresh: true,
        search: true,
        uniqueId: "group_id",
        pageSize : 10,
        pageList : [ 10, 25, 50, 100, 'all'],
        sortable: false,
        detailView: true,
        columns: [{
            field: 'group_id',
            title: '主机ID',
            align: 'center',
            width: '10',
            widthUnit: '%'
        }, {
            field: 'group_name',
            title: '主机组名',
            align: 'left',
            width: '30',
            widthUnit: '%'
        }, {
            field: 'group_type',
            title: '主机组类型',
            align: 'left',
            width: '30',
            widthUnit: '%'
        }, {
            field: 'group_oper',
            title: '操作',
            align: 'center',
            width: '25',
            widthUnit: '%',
            events: groupEvents,
            formatter: addgroupButton
        }],
        onExpandRow: function(index,row, $detail){
            var group_name = row.group_name;
            var group_type = row.group_type;
            var host_sub_table = $detail.html('<table id="host_sub_table"></table>').find('table');
            $(host_sub_table).bootstrapTable({
                url: '/inventory/getdata/hostdata',
                contentType: 'application/json',
                queryParams: {'group_name': group_name, 'group_type': group_type},
                pagination: false,
                uniqueId: "host_id",
                columns: [{
                    field: 'host_id',
                    title: '主机ID',
                    align: 'center'
                }, {
                    field: 'host_name',
                    title: '主机名',
                    align: 'left'
                }, {
                    field: 'host_ip',
                    title: '主机IP',
                    align: 'left'
                }, {
                    field: 'host_user',
                    title: '用户名',
                    align: 'left'
                }, {
                    field: 'host_port',
                    title: 'SSH端口',
                    align: 'left'
                }, {
                    field: 'host_os',
                    title: '操作系统',
                    align: 'left'
                }, {
                    field: 'host_group_name',
                    title: '子主机组',
                    align: 'left'
                }, {
                    field: 'host_oper',
                    title: '操作',
                    align: 'center',
                    events: hostEvents,
                    formatter: addhostButton
                }]
            })
        }
    })
};

// 增加父表操作按钮
function addgroupButton(value, row, index){
    return ['<button id="deleteGroup" type="button" class="btn btn-default btn-danger">删除</button>']
};

//增加子表操作按钮
function addhostButton(value, row, index){
    return ['<button id="deleteHost" type="button" class="btn btn-default btn-danger">删除</button>']
}

// 删除主机组
function deletegroup(type, id){
    $.ajax({
        url: "/inventory/delete",
        type: "POST",
        contentType: "application/json;charset=utf-8",
        data: JSON.stringify({"type": type, "id": id}),
        dataType: "json",
        success: function(response){
            if (response.code != 0){
                alert("删除失败！"+response.message);
            }else{
                alert("删除"+response.message+"成功！");
                $('#confirmmodal').modal('hide');
            }
        },
        error: function(){
            alert("server error!");
        }
    })
};

// 注册字表操作事件
var hostEvents = {
    'click #deleteHost': function (e, value, row, index){
        $('#confirmmodal').modal();
        var deletegroup_b = document.getElementById('confirm_button');
        deletegroup_b.onclick = function(){
            deletegroup("host", row.host_id);
        };
        document.getElementById('confirm_info').innerText = "确认删除主机？"
    }
};

// 新增主机
$('#add_host').click(function (){
    console.log("add host modal");
    $('#addhostmodal').modal({backdrop: 'static', keyboard: false});
});

// 增加主机组
$('#add_host_group').click(function (){
    console.log("add host group modal.");
    $('#addgroupmodal').modal();
    $.ajax({
        type: "GET",
        url: "/inventory/getdata/childgroup",                          
        dataType: "json",
        success: function(response){
            if (response.code != 0){                                            
                alert("获取数据失败！" + response.message);
            }else{
                var select_str = '';                
                $('#childgroup').empty();
                for (var i=0; i<response.data.length; i++){
                    select_str += '<option value="'+response.data[i].group_id+'">'+response.data[i].group_name+'</option>'
                }
                $('#childgroup').append(select_str);
                $('#childgroup').selectpicker('refresh');
            }
        },
        error: function(){
            alert("server error!")
        }
    })
});

// 提交新增主机
$('#commit_addhost').click(function (){
    var req_data = {
        "host_name": $('#add_host_name').val(),
        "host_ip": $('#add_host_ip').val(),
        "host_port": $('#add_host_port').val(),
        "host_user": $('#add_host_user').val(),
        "host_os": $('#add_host_os').val(),
        "host_group": $('#add_host_c_group').val(),
        "host_note": $('#add_host_commit').val()
    };
    if (req_data.host_name == "" || req_data.host_ip == "" || req_data.host_port == "" || req_data.host_user == "" || req_data.host_os == "" || req_data.host_group == "" || req_data.host_note == ""){
        alert("输入项不允许为空！");
        return;
    };
    var ip_regex = /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/;
    var port_regex = /^[1-9]+[0-9]*]*$/;
    if (! ip_regex.test(req_data.host_ip)){
        alert("ip 填写错误！");
        return;
    };
    if (! port_regex.test(req_data.host_port)){
        alert("port 填写错误！");
        return;
    };
    console.log(req_data);
    $.ajax({
        url: '/inventory/add/host',
        type: 'POST',
        data: JSON.stringify(req_data),
        contentType: "application/json;charset=utf-8",
        dataType: 'json',
        success: function(response){
            if (response.code !=0 ){
                alert("添加主机失败！"+ response.message);
            }else{
                alert("添加主机成功!\n为了正常使用请更新主机文件\n且添加server的ssh公钥到主机！");
                $('#addhostmodal').modal('hide');
            }
        },
        error: function(){
            alert("server error!");
        }
    })
});

// 提交新增主机组
$('#commit_addgroup').click(function (){
    var p_group_name = $("#add_group_name").val();
    var c_groups = $('#childgroup').selectpicker('val');
    if (p_group_name == "" || c_groups == null){
        alert("输入项不允许为空！");
        return;
    }
    var req_data = {
        "group_name": p_group_name,
        "child_group": c_groups
    }
    console.log(req_data);
    $.ajax({
        url: "/inventory/add/group",
        type: 'POST',
        contentType: "application/json;charset=utf-8",
        data: JSON.stringify(req_data),
        dataType: 'json',
        success: function(response){
            if (response.code != 0){
                alert("增加父主机组失败！"+ response.message);
            }else{
                alert("增加父主机组成功！\n为了正常使用请更新主机组文件！");
            }
        },
        error: function(){
            alert("server error!")
        }
    })
});

// 更新服务器ansible主机文件
$('#update_host_file').click(function (){
    $.ajax({
        url: "/inventory/update/hostfile",
        type: 'GET',
        dataType: 'json',
        success: function(response){
            if (response.code != 0){
                alert("更新主机文件失败！"+ response.message);
            }else{
                alert("更新主机文件成功！");
            }
        },
        error: function(){
            alert("server error!")
        }
    })
});     

// 更新服务器ansible主机组文件
$('#update_group_file').click(function (){    
    $.ajax({
        url: "/inventory/update/groupfile",
        type: 'GET',
        dataType: 'json',
        success: function(response){
            if (response.code != 0){
                alert("更新主机组文件失败！"+ response.message);
            }else{
                alert("更新主机组文件成功！");
            }
        },
        error: function(){
            alert("server error!")
        }
    })
});     
