// The button of the network of the integration tests: "Setup Docker" when it is down, "Stop Docker" when it is up. The commands are the
// ones of the tasks of .vscode/tasks.json, which the button runs.

const childProcess = require('child_process');
const vscode = require('vscode');
const { createButton } = require('./button');
const running = require('./running');

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
// between two checks, while the window has the focus. A check is a process that ends on its own: one that waits for the events of docker
// would stay when the extensions of VS Code crash
const CHECK_MS = 5000;
// a check that does not answer is given up
const TIMEOUT_MS = 10000;

function activate(context) {
    const cwd = vscode.workspace.workspaceFolders[0].uri.fsPath;
    const show = createButton(context, 50.3, 'Docker Test Network');
    let shown = SETUP;
    let up = false;
    let checks = 0;
    let pending = 0;
    let disposed = false;

    function render() {
        // while one of the two tasks runs, its button stays, with a spinning icon
        const busy = [SETUP, STOP].find(button => running.isRunning(button.task));
        shown = busy || (up ? STOP : SETUP);
        show({
            text: `$(${busy ? 'sync~spin' : shown.icon}) ${shown.label}`,
            tooltip: shown.tooltip,
            command: COMMAND,
            waitsFor: busy ? undefined : running.blocker([SETUP.task, STOP.task]),
        });
    }

    function check() {
        const current = ++checks;
        pending++;
        childProcess.execFile('docker', PS_ARGS, { cwd, timeout: TIMEOUT_MS }, (error, stdout) => {
            pending--;
            // an older check that ends late does not replace the result of a newer one
            if (disposed || current !== checks) {
                return;
            }
            // without docker the button is the one of the setup, whose task says what is wrong
            up = !error && stdout.trim() !== '';
            render();
        });
    }

    // for the changes made from a terminal
    const timer = setInterval(() => {
        if (vscode.window.state.focused && pending === 0) {
            check();
        }
    }, CHECK_MS);

    running.onChange(render);
    context.subscriptions.push(
        vscode.commands.registerCommand(COMMAND, () => vscode.commands.executeCommand('workbench.action.tasks.runTask', shown.task)),
        vscode.tasks.onDidEndTask(() => check()),
        vscode.window.onDidChangeWindowState(state => {
            if (state.focused) {
                check();
            }
        }),
        {
            dispose() {
                disposed = true;
                clearInterval(timer);
            },
        },
    );

    render();
    check();
}

module.exports = { activate };
