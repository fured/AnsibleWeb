/*
* Author: fured
* Desc: 任务集页面相关操作
*/
var all_data;
// 增加任务集
$('#add_taskset').click(function(){
    $('#addmodal').modal();
    console.log("add task set modal");
    var package_range = ["5", "10", "30", "all"];
    document.getElementById("packagetimerange").options.length=0;
    package_range.forEach(function (item, index){
       document.getElementById("packagetimerange").options.add(new Option("选择"+item+"天的代码包", item))
    });
    var package_time_range = $('#packagetimerange').val();
    get_taskset_data(package_time_range);
    var task_p_type = ["projects", "softs"];
    document.getElementById("task_p_type").options.length=0;
    task_p_type.forEach(function (item, index) {
        document.getElementById("task_p_type").options.add(new Option(item, item))
    });
    get_task_p_project("type");
    var inventory_type = ["host", "group"];
    document.getElementById("task_inventory_type").options.length=0;
    inventory_type.forEach(function (item, index) {
       document.getElementById("task_inventory_type").options.add(new Option(item, item))
    });
    get_task_inventory("type");
    $('#task_exeorder').val("1");
});

function get_task_p_projects(val){
    console.log(val.id.split('_').pop());
    get_task_p_project(val.id.split('_').pop());

}

function get_task_p_project(index){
    // 获取对应项目
    console.log("update yml project");
    if (index == "type"){
        var suffix = "";
    }else{
        var suffix = "_" + index;
    }
    var task_p_type = $("#task_p_type"+suffix).val();
    var all_projects = new Array();
    all_data.playbook.forEach(function (item, index){
        if (item.pb_type == task_p_type && all_projects.indexOf(item.pb_project_name) == -1){
            all_projects.push(item.pb_project_name)
        }
    });
    document.getElementById("task_p_project"+suffix).options.length=0;
    document.getElementById("task_p_name"+suffix).options.length=0;
    all_projects.forEach(function (item, index){
        document.getElementById("task_p_project"+suffix).options.add(new Option(item, item))
    });
    get_task_p_name(index);
}

function get_task_p_names(val){
    console.log(val.id.split('_').pop());
    get_task_p_name(val.id.split('_').pop());
}

function get_task_p_name(index){
    // 获取项目对应的剧本
    console.log("update playbook name");
    if (index == "type" || index == "project"){
        var suffix = "";
    }else{
        var suffix = "_" + index;
    }
    var task_p_type = $("#task_p_type"+suffix).val();
    var project_name = $("#task_p_project"+suffix).val();
    var all_playbook = new Array();
    all_data.playbook.forEach(function (item, index) {
        if (item.pb_type == task_p_type && item.pb_project_name == project_name){
            all_playbook.push({
                "file_name": item.pb_file_name,
                "playbook_id": item.playbook_id
            })
        }
    });
    document.getElementById("task_p_name"+suffix).options.length=0;
    all_playbook.forEach(function (item, index) {
        document.getElementById("task_p_name"+suffix).options.add(new Option(item.file_name, item.playbook_id))
    })
}

function get_task_inventorys(val){
    console.log(val.id.split('_').pop());
    get_task_inventory(val.id.split('_').pop());
}

function get_task_inventory(index){
    console.log("update inventory");
    if (index == "type"){
        var suffix = "";
    }else{
        var suffix = "_" + index;
    }
    var inventory_type = $("#task_inventory_type"+suffix).val();
    var all_inventory = new Array();
    document.getElementById("task_inventory"+suffix).options.length=0;
    if (inventory_type == "host"){
        all_data.inventory.host.forEach(function (item, index) {
            document.getElementById("task_inventory"+suffix).options.add(new Option(item.host_name, item.host_id))
        })
    };
    if (inventory_type == "group"){
        all_data.inventory.group.forEach(function (item, index) {
            document.getElementById("task_inventory"+suffix).options.add(new Option(item.group_name, item.group_id))
        })
    };
}

// 获取根据选择天数代码包
$('#packagetimerange').change(function(){
    var package_time_range = $('#packagetimerange').val();
    update_package_options(package_time_range);
});

// 获取生成任务集的数据
function get_taskset_data(time_range){
    $.ajax({
        type: "POST",
        url: "/tasks/taskset/getalldata",
        async: false,
        contentType: "application/json;charset=utf-8",
        data: JSON.stringify({"range": time_range}),
        dataType: "json",
        success: function(response){
            if (response.code != 0){
                alert("获取数据失败！"+response.message);
            }else{
                var all_task_select = document.querySelectorAll('#task_package');
                for (var i=0; i<all_task_select.length; i++){
                    all_task_select[i].options.length=0;
                    for (var j=0;j<response.data.package.length; j++){
                        all_task_select[i].options.add(new Option(response.data.package[j].pg_file_name, response.data.package[j].package_id));
                    }
                }
                all_data = response.data;
            }
        },
        error: function(){
            alert("服务器错误");
        }
    })
}

// 更新代码包下拉框
function update_package_options(time_range){
    $.ajax({
        type: "POST",
        url: "/tasks/taskset/getalldata",
        contentType: "application/json;charset=utf-8",
        data: JSON.stringify({"range": time_range}),
        dataType: "json",
        success: function(response){
            if (response.code != 0){
                alert("获取数据失败！"+ response.message);
            }else{
                var all_task_select = document.querySelectorAll('#task_package');
                for (var i=0; i<all_task_select.length; i++){
                    all_task_select[i].options.length=0;
                    for (var j=0;j<response.data.package.length; j++){
                        all_task_select[i].options.add(new Option(response.data.package[j].pg_file_name, response.data.package[j].package_id));
                    }
                }
            }
        },
        error: function(response){
            alert("服务器错误");
        }
    })
};

// 增加任务为任务集
var task_num = 1;
$('#con_add_task').click(function(){
    var e = document.getElementById("addtasks");
    var div = document.createElement("div");
    div.className = "form-group";
    task_num++;
    div.id = "addtasks_" + task_num;
    div.innerHTML = e.innerHTML;
    div.childNodes[3].childNodes[3].id = "task_p_type_" + task_num;
    div.childNodes[3].childNodes[5].id = "task_p_project_" + task_num;
    div.childNodes[3].childNodes[7].id = "task_p_name_" + task_num;
    div.childNodes[7].childNodes[3].id = "task_inventory_type_" + task_num;
    div.childNodes[7].childNodes[5].id = "task_inventory_" + task_num;
    div.childNodes[9].childNodes[3].id = "task_exeorder_" + task_num;
    document.getElementById("add_taskset_form").appendChild(div);
    get_task_p_project(task_num);
    get_task_inventory(task_num);
    $("#task_exeorder_"+task_num).val(task_num);
});
$('#del_task').click(function(){
    var id = "addtasks_" + (task_num).toString();
    var e = document.getElementById(id);
    document.getElementById("add_taskset_form").removeChild(e);
    task_num--;
});

// 提交任务集
$('#commit_taskset').click(function(){
    var taskset_name = $('#tasksetname').val();
    //console.log(taskset_name);
    //console.log(task_num);
    var tasks = new Array();
    var task = {
        "task_name": document.getElementById("addtasks").getElementsByTagName("input").task_name.value,
        "exe_order": document.getElementById("addtasks").getElementsByTagName("input").task_exeorder.value,
        "playbook_id": document.getElementById("addtasks").getElementsByTagName("select").task_p_name.value,
        "package_id": document.getElementById("addtasks").getElementsByTagName("select").task_package.value,
        "inventory": {
            "type": document.getElementById("addtasks").getElementsByTagName("select").task_inventory_type.value,
            "id": document.getElementById("addtasks").getElementsByTagName("select").task_inventory.value
        }
    };
    tasks[0] = task;
    for (var i=2; i<=task_num; i++){
        tasks[i-1] = {
            "task_name": document.getElementById("addtasks_"+i).getElementsByTagName("input").task_name.value,
            "exe_order": $("#task_exeorder_"+ i).val(),
            "playbook_id": $("#task_p_name_"+i).val(),
            "package_id": document.getElementById("addtasks_"+i).getElementsByTagName("select").task_package.value,
            "inventory": {
                "type": $("#task_inventory_type_"+i).val(),
                "id": $("#task_inventory_"+i).val()
            }
        }
    }
    // 表单校验
   if (taskset_name == ""){
       alert("任务集名不允许为空！");
       return;
   }
   for (var i=0; i<tasks.length; i++){
       if (tasks[i].task_name == "" || tasks[i].exe_order == "" || tasks[i].playbook_id == "" || tasks[i].package_id == "" || tasks[i].inventory.type == "" || tasks[i].inventory.id == ""){
           alert("不允许有字段为空!");
           return;
       };
       var re_num = /^[1-9]+[0-9]*]*$/;
       if (!re_num.test(tasks[i].exe_order)){
           alert("执行顺序必须是数字!");
           return;
       };
   }
   //上传任务到服务器
   $.ajax({
       type: "POST",
       url: "/tasks/taskset/payload",
       contentType: "application/json;charset=utf-8",
       data: JSON.stringify({"task_set_name": taskset_name, "tasks": tasks}),
       dataType: "json",
       success: function(response){
           if (response.code != 0){
               alert("新增任务集失败！"+ response.message);
           }else{
               alert("新增任务集成功！");
               $('#addmodal').modal('hide');
           }

       }
   })
});

// 更新服务器代码包到数据库
$('#ref_packages').click(function(){
    $.ajax({
        type: "GET",
        url: "/tasks/package/update",
        dataType: "json",
        success: function(response){
            if (response.code != 0){
                alert("更新失败！"+ response.message);
            }else{
                alert("更新成功！");
            }
        },
        error: function(){
            alert("server error!");
        }
    })
});
