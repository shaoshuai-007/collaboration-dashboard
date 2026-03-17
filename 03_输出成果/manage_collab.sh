#!/bin/bash

case "$1" in
    start)
        cd /root/.openclaw/workspace/03_输出成果
        nohup python3 collaboration_dashboard.py > /tmp/collab.log 2>&1 &
        sleep 2
        echo "✅ 服务已启动"
        netstat -tlnp | grep 5001
        ;;
    stop)
        pkill -f collaboration_dashboard
        echo "✅ 服务已停止"
        ;;
    restart)
        pkill -f collaboration_dashboard
        sleep 2
        cd /root/.openclaw/workspace/03_输出成果
        nohup python3 collaboration_dashboard.py > /tmp/collab.log 2>&1 &
        sleep 2
        echo "✅ 服务已重启"
        netstat -tlnp | grep 5001
        ;;
    status)
        echo "=== 进程状态 ==="
        ps aux | grep collaboration_dashboard | grep -v grep || echo "服务未运行"
        echo ""
        echo "=== 端口状态 ==="
        netstat -tlnp | grep 5001 || echo "端口未监听"
        ;;
    log)
        tail -50 /tmp/collab.log
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|log}"
        ;;
esac
