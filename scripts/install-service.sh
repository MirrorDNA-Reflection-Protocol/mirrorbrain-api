#!/bin/bash
# Install/manage MirrorBrain API service

PLIST_NAME="ai.mirrordna.brain.api"
PLIST_SRC="$(dirname "$0")/../launchagent/${PLIST_NAME}.plist"
PLIST_DST="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"
DATA_DIR="$HOME/.mirrordna/brain"

case "${1:-status}" in
    install)
        # Create data directory
        mkdir -p "$DATA_DIR/data"

        # Copy plist
        cp "$PLIST_SRC" "$PLIST_DST"

        # Load service
        launchctl load "$PLIST_DST"
        echo "MirrorBrain API installed and started on port 8100"
        echo "API docs: http://localhost:8100/docs"
        ;;

    uninstall)
        launchctl unload "$PLIST_DST" 2>/dev/null
        rm -f "$PLIST_DST"
        echo "MirrorBrain API uninstalled"
        ;;

    start)
        launchctl start "$PLIST_NAME"
        echo "MirrorBrain API started"
        ;;

    stop)
        launchctl stop "$PLIST_NAME"
        echo "MirrorBrain API stopped"
        ;;

    restart)
        launchctl stop "$PLIST_NAME"
        sleep 1
        launchctl start "$PLIST_NAME"
        echo "MirrorBrain API restarted"
        ;;

    status)
        if launchctl list | grep -q "$PLIST_NAME"; then
            echo "MirrorBrain API is loaded."
            launchctl list "$PLIST_NAME"
        else
            echo "MirrorBrain API is not loaded."
        fi
        ;;

    logs)
        tail -f "$DATA_DIR/api.log"
        ;;

    *)
        echo "Usage: $0 {install|uninstall|start|stop|restart|status|logs}"
        exit 1
        ;;
esac
