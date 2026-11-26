// The button of the network of the integration tests: "Setup Docker" when it is down, "Stop Docker" when it is up. The commands are the
// ones of the tasks of .vscode/tasks.json, which the button runs.

const childProcess = require('child_process');
const vscode = require('vscode');

const SETUP = {
    task: 'tests: setup docker',
    label: 'Setup Docker',
    icon: 'play',
    tooltip: 'setup docker environment for integration tests',
};
const STOP = {
    task: 'tests: stop docker',
    label: 'Stop Docker',
    icon: 'stop-circle',
    tooltip: 'stop the Docker environment for integration tests',
};
const COMMAND = 'moneroPython.runDockerTask';
// the containers of the network that run, one id for each
const PS_ARGS = ['compose', '-f', 'tests/docker-compose.yml', 'ps', '--quiet', '--status', 'running'];
// a line when a container starts or goes away, also the ones started from a terminal
const EVENTS_ARGS = [
    'events', '--format', '{{.Actor.ID}}', '--filter', 'type=container',
    '--filter', 'event=start', '--filter', 'event=die', '--filter', 'event=destroy',
];
// the containers of the network change together: one check for all of their events
const DEBOUNCE_MS = 500;
// docker events ends when the daemon of docker is not running
const RETRY_MS = 30000;

function activate(context) {
    const cwd = vscode.workspace.workspaceFolders[0].uri.fsPath;
    const item = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 50);
    item.name = 'Docker Test Network';
    item.command = COMMAND;

    // the names of the tasks that run now
    const running = new Set(vscode.tasks.taskExecutions.map(execution => execution.task.name));
    let shown = SETUP;
    let up = false;
    let checks = 0;
    let events;
    let checkTimer;
    let retryTimer;
    let disposed = false;

    function render() {
        // while one of the two tasks runs, its button stays, with a spinning icon
        const busy = [SETUP, STOP].find(button => running.has(button.task));
        shown = busy || (up ? STOP : SETUP);
        item.text = `$(${busy ? 'sync~spin' : shown.icon}) ${shown.label}`;
        item.tooltip = shown.tooltip;
        item.show();
    }

    function check() {
        const current = ++checks;
        childProcess.execFile('docker', PS_ARGS, { cwd }, (error, stdout) => {
            // an older check that ends late does not replace the result of a newer one
            if (disposed || current !== checks) {
                return;
            }
            // without docker the button is the one of the setup, whose task says what is wrong
            up = !error && stdout.trim() !== '';
            render();
        });
    }

    function scheduleCheck() {
        clearTimeout(checkTimer);
        checkTimer = setTimeout(check, DEBOUNCE_MS);
    }

    function watch() {
        events = childProcess.spawn('docker', EVENTS_ARGS, { cwd, stdio: ['ignore', 'pipe', 'ignore'] });
        events.stdout.on('data', scheduleCheck);
        // docker is not installed: "close" follows
        events.on('error', () => {});
        events.on('close', () => {
            if (!disposed) {
                scheduleCheck();
                retryTimer = setTimeout(watch, RETRY_MS);
            }
        });
    }

    context.subscriptions.push(
        item,
        vscode.commands.registerCommand(COMMAND, () => vscode.commands.executeCommand('workbench.action.tasks.runTask', shown.task)),
        // also when the task runs as a dependency of another, as of "tests: integration"
        vscode.tasks.onDidStartTask(event => {
            running.add(event.execution.task.name);
            render();
        }),
        vscode.tasks.onDidEndTask(event => {
            running.delete(event.execution.task.name);
            render();
            scheduleCheck();
        }),
        {
            dispose() {
                disposed = true;
                clearTimeout(checkTimer);
                clearTimeout(retryTimer);
                events.kill();
            },
        },
    );

    render();
    check();
    watch();
}

module.exports = { activate };
