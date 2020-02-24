var tasksetEvents = {
    'click #runtaskset':function (e, value, row, index){
        run_check_taskset("run", row, index);
    },
    'click #checktaskset':function (e, value, row, index){
        run_check_taskset("check", row, index);
    },
    'click #runrevoke':function (e, value, row, index){
        revoke_taskset("run", row.taskset_cid);
    },
    'click #checkrevoke':function (e, value, row, index){
        revoke_taskset("check", row.taskset_c_cid);
    },
    'click #setdetail':function (e, value, row, index){
        $('#taskset_table').bootstrapTable('expandRow', index); 
    }
};
$('#taskset_table').bootstrapTable({
    url: 'tasks/taskset/obtaindata',
    method: 'post',
    contentType: 'application/json',
    toolbar: '#toolbar',
    sidePagination: "server",
    pagination: true,
    showRefresh: true,
    search: true,
    uniqueId: "taskset_id",
    pageSize : 10,
    pageList : [ 10, 25, 50, 100, 'all' ],
    sortable: true,
    sortOrder: 'desc',
    sortName: 'taskset_id',
    detailView: true,
    columns: [{
        field: 'taskset_id',
        title: '任务集ID',
        align: 'center',
        width: '6',
        widthUnit: '%'
    }, {
        field: 'taskset_name',
        title: '任务集名字',
        align: 'left',
        width: '22',
        widthUnit: '%'
    }, {
        field: 'taskset_cid',
        title: '执行ID',
        align: 'center',
        width: '20',
        widthUnit: '%'

    }, {
        field: 'taskset_c_cid',
        title: 'CheckID',
        align: 'center',
        width: '20',
        widthUnit: '%'
    }, {
        field: 'taskset_status',
        title: '状态',
        align: 'center',
        width: '10',
        widthUnit: '%'
    }, {
        field: 'check_status',
        title: 'Check状态',
        align: 'center',
        width: '10',
        widthUnit: '%'
    }, {
        field: 'taskset_oper',
        title: '操作',
        align: 'center',
        width: '12',
        widthUnit: '%',
        events: tasksetEvents,
        formatter: addFunctionAlty
    }],
    onExpandRow: function(index, row, $detail){
        var t_set_id = row.taskset_id;
        var cur_table = $detail.html('<table id="task_table"></table>').find('table');
        $(cur_table).bootstrapTable({
            url: "/tasks/taskset/obtaintasks",
            contentType: 'application/json',
            queryParams: {'task_set_id': t_set_id },
            detailView: false,
            pagination: false,
            uniqueId: "task_id",
            columns: [{
                field: 'task_id',
                title: '任务ID',
                align: 'center'
            }, {
                field: 'task_set_id',
                title: '任务集ID',
                visible: false
            }, {
                field: 'playbook',
                title: '剧本',
                align: 'left'
            }, {
                field: 'package',
                title: '代码包',
                align: 'left'
            }, {
                field: 'inventory_type',
                title: '执行对象类型',
                align: 'center'
            }, {
                field: 'inventory',
                title: '执行对象',
                align: 'left'
            }, {
                field: 'task_status',
                title: '状态',
                align: 'center'
            }, {
                field: 'check_status',
                title: 'check状态',
                align: 'center'
            }, {
                filed: 'task_oper',
                title: '操作',
                align: 'center',
                events: taskEvents,
                formatter: addButton
            }]
        })
    }
})

// 父表 数据后面增加操作按钮
function addFunctionAlty(value, row, index){
    var operation = new Array()
    if (row.taskset_status != 'STARTED' && row.taskset_status != 'COMPLETE' && row.taskset_status != 'PENDING' && row.check_status != 'PENDING' && row.check_status != 'STARTED'){
       operation.push('<button id="runtaskset" type="button" class="btn btn-default btn-info">Run</button>')
    }
    if (row.check_status != 'STARTED' && row.check_status != 'COMPLETE' && row.check_status != 'PENDING' && row.taskset_status != 'PENDING' && row.taskset_status != 'STARTED'){
        operation.push('<button id="checktaskset" type="button" class="btn btn-default btn-warning">Check</button>')
    }
    if (row.check_status == 'STARTED'){
        operation.push('<button id="checkrevoke" type="button" class="btn btn-default btn-danger">Check-revoke</button>')
    }
    if (row.taskset_status == 'STARTED'){
        operation.push('<button id="runrevoke" type="button" class="btn btn-default btn-danger">Run-revoke</button>')
    }
    if (row.taskset_status == 'COMPLETE' && row.check_status == 'COMPLETE'){
        operation.push('<button id="setdetail" type="button" class="btn btn-default btn-inverse">详情</button>')
    }
    return operation
}

// 增加子表按钮
function addButton(value, row, index){
    var oper = new Array()
    if (row.task_status != 'PENDING' &&  row.task_status != 'REVOKED' && row.task_status != 'NEW'){
        oper.push('<button id="runlog" type="button" class="btn btn-default btn-info">运行日志</button>')
    }
    if (row.check_status != 'PENDING' && row.check_status != 'REVOKED' && row.check_status != 'NEW'){
        oper.push('<button id="checklog" type="button" class="btn btn-default btn-warning">Check日志</button>')
    }
    return oper
}

//子表操作事件
var taskEvents = {
    'click #runlog':function (e, value, row, index){
        console.log("log modal");
        $('#logmodel').modal();
        $("#logscroll").empty();
        get_run_log(row, "run", 0);
    },
    'click #checklog':function (e, value, row, index){
        $('#logmodel').modal();
        $("#logscroll").empty();
        get_run_log(row, "check", 0);
    }
};

// 读取正式运行或者检查日志
function get_run_log(row, type, seek){
        if (type == "run"){
            var log_url = "/tasks/taskset/getrunlog";
        }else{
            var log_url = "/tasks/taskset/getchecklog";
        };
        console.log("seek: "+seek);
        $.ajax({
            type: "POST",
            url: log_url,
            contentType: "application/json;charset=utf-8",
            data: JSON.stringify({ "seek": seek, "task_set_id": row.task_set_id, "task_id": row.task_id}),
            dataType:"json",
            success: function(response){
                if (response.code != 0){
                    alert("获取执行日志失败！"+response.message);
                }
                else{
                    var read_flag = response.data.read_flag;
                    //var read_flag = true;
                    var run_log = response.data.log;
                    var new_seek = response.data.new_seek;
                    $("#logscroll").append(run_log);
                    document.getElementById("logscroll").scrollTop = document.getElementById("logscroll").scrollHeight;
                    //console.log(run_log);
                    if (read_flag == false){
                       $("#logscroll").append('\n Log End.\n');
                        document.getElementById("logscroll").scrollTop = document.getElementById("logscroll").scrollHeight;
                    }else{
                        console.log("new_seek:"+new_seek);
                        setTimeout(function(){get_run_log(row, type, new_seek)}, 5000);
                    }
            }},
            error: function(){
                alert("获取执行日志失败！");
            }
        })
}

// 开始运行正式或检查任务
function run_check_taskset(run_type, row, index){
        $.ajax({
            type: 'POST',
            url: 'tasks/taskset/runcheck',
            contentType: "application/json;charset=utf-8",
            data: JSON.stringify({"type": run_type, "task_set_id": row.taskset_id}),
            dataType: "json",
            success: function(response){
               if (response.code != 0){
                   alert("运行任务集失败！"+ response.message);
               }else{
                   alert("任务集进入队列马上运行！");
                   console.log(run_type);
                   if (run_type == "run"){
                       
                       $('#taskset_table').bootstrapTable('updateCell', {index: index, field: 'taskset_cid', value: response.data.celery_id});
                       $('#taskset_table').bootstrapTable('updateCell', {index: index, field: 'taskset_status', value: response.data.status});
                       $('#taskset_table').bootstrapTable('updateCell', {index: index, field: 'taskset_oper'});
                       refesh_run_check_status("run", response.data.celery_id, index);
                   };
                   if (run_type == "check"){
                       console.log(index);
                       console.log(response.data.celery_id);
                       $('#taskset_table').bootstrapTable('updateCell', {index: index, field: 'taskset_c_cid', value: response.data.celery_id});
                       $('#taskset_table').bootstrapTable('updateCell', {index: index, field: 'check_status', value: response.data.status});
                       $('#taskset_table').bootstrapTable('updateCell', {index: index, field: 'taskset_oper'});
                       refesh_run_check_status("check", response.data.celery_id, index);
                   }

               }
            },
            error: function(){
                alert("运行任务集失败！");
            }
        })
}

// 刷新正在运行的检查或者正式任务的状态
function refesh_run_check_status(run_type, celery_id, index){
    console.log('start refesh');
    $.ajax({
        type: "POST",
        url: "/tasks/taskset/currentstatus",
        contentType: "application/json;charset=utf-8",
        data: JSON.stringify({"type": run_type, "celery_id": celery_id}),
        dataType: "json",
        success: function(response){
            if (response.code != 0){
                alert("获取执行状态失败:"+response.message);
            }else{
                if (run_type == "run"){
                    $('#taskset_table').bootstrapTable('updateCell', {index: index, field: 'taskset_status', value: response.data.task_set.status});
                    $('#taskset_table').bootstrapTable('expandRow', index);
                    for (var i=0,len=response.data.tasks.length; i<len; i++){
                        $('#task_table').bootstrapTable('updateCellByUniqueId', {task_id: response.data.tasks[i].task_id, field: 'task_status', value: response.data.tasks[i].status});
                        $('#task_table').bootstrapTable('updateCellByUniqueId', {task_id: response.data.tasks[i].task_id, field: 'task_oper'});
                    }
                    $('#taskset_table').bootstrapTable('expandRow', index);
                };
                if (run_type == "check"){
                    console.log("check----")
                    $('#taskset_table').bootstrapTable('updateCell', {index: index, field: 'check_status', value: response.data.task_set.status});
                    $('#taskset_table').bootstrapTable('expandRow', index);
                    for (var i=0,len=response.data.tasks.length; i<len; i++){
                        $('#task_table').bootstrapTable('updateCellByUniqueId', {task_id: response.data.tasks[i].task_id, field: 'check_status', value: response.data.tasks[i].status});
                        $('#task_table').bootstrapTable('updateCellByUniqueId', {task_id: response.data.tasks[i].task_id, field: 'task_oper'});
                    }
                    $('#taskset_table').bootstrapTable('expandRow', index);
                };
                if (response.data.task_set.status == 'PENDING' || response.data.task_set.status == 'STARTED'){
                    setTimeout(function(){refesh_run_check_status(run_type, celery_id, index)}, 5000);
                }
            }
        },
        error: function(){
            alert("获取执行状态失败,server errr!");
        }
    })
}

// 取消正在运行的检查或者正式任务
function revoke_taskset(run_type, celery_id){
    console.log(run_type);
    console.log(celery_id);
    $.ajax({
        type: "POST",
        url: "/tasks/taskset/revoke",
        contentType: "application/json;charset=utf-8",
        data: JSON.stringify({"type": run_type, "celery_id": celery_id}),
        dataType: "json",
        success: function(response){
            if (response.code != 0){
                alert("撤销失败:"+response.message);
            }else{
                alert("撤销成功");
            }
        },
        error: function(){
            alert("server errr!");
        }

    })
}
