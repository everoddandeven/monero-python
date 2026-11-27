// The popups of the task "lint: links" of .vscode/tasks.json, the one of the button "Lint Docs": when it ends, one for each of the
// first problems that its problem matcher found, with a button that opens it, one for the others, one for the redirects and one for
// each hint of lychee.

const vscode = require('vscode');

const TASK = 'lint: links';
// the "source" of the problem matcher of the task, which tells its problems from the others
const SOURCE = 'lychee';
const TITLE = 'Lint Docs';
// the copy of the output that the task writes, in the folder of the workspace
const LOG = ['.cache', 'lint-links.log'];
// a line of lychee about the whole check
const HINT = /^Hint: (.+)$/gm;
// the count of the redirects in the last line of the report: with -vv, their details are lines of the output
const REDIRECTS = /(\d+) Redirects\b/;
// the colors of a terminal
const ANSI = /\u001b\[[0-9;]*m/g;
// the popups of single problems, VS Code hides the ones that are too many
const MAX_POPUPS = 3;
// the problems of the matcher reach the extensions a moment after the end of the task
const WAIT_MS = 1000;

function findProblems() {
    return vscode.languages.getDiagnostics().flatMap(([uri, diagnostics]) =>
        diagnostics.filter(diagnostic => diagnostic.source === SOURCE).map(diagnostic => ({ uri, diagnostic })));
}

function popup(isError, message, button, action) {
    const show = isError ? vscode.window.showErrorMessage : vscode.window.showWarningMessage;
    show(message, button).then(choice => {
        if (choice === button) {
            action();
        }
    });
}

const isError = problem => problem.diagnostic.severity === vscode.DiagnosticSeverity.Error;

const showTerminal = () => vscode.commands.executeCommand('workbench.action.terminal.focus');

// the warnings about the whole check, from the copy of the output
async function findWarnings() {
    const file = vscode.Uri.joinPath(vscode.workspace.workspaceFolders[0].uri, ...LOG);
    try {
        const output = Buffer.from(await vscode.workspace.fs.readFile(file)).toString('utf8').replace(ANSI, '');
        const warnings = Array.from(output.matchAll(HINT), match => match[1].trim());
        const redirects = Number(REDIRECTS.exec(output)?.[1] ?? 0);
        if (redirects > 0) {
            warnings.unshift(`${redirects} redirect${redirects === 1 ? '' : 's'}, the terminal shows where they go`);
        }
        return warnings;
    } catch {
        // no copy of the output: no warnings
        return [];
    }
}

async function reportWarnings(exitCode) {
    // no exit code: the task was stopped, and the copy is not whole
    if (exitCode !== undefined) {
        for (const warning of await findWarnings()) {
            popup(false, `${TITLE}: ${warning}`, 'Show Terminal', showTerminal);
        }
    }
}

function reportProblems(exitCode) {
    // errors first
    const problems = findProblems().sort((a, b) => a.diagnostic.severity - b.diagnostic.severity);
    if (problems.length === 0) {
        // no exit code: the task was stopped. Another one than 0 without problems: the check did not run, as without a network
        if (exitCode !== undefined && exitCode !== 0) {
            popup(true, `${TITLE} failed with exit code ${exitCode}`, 'Show Terminal', showTerminal);
        }
        return;
    }
    for (const problem of problems.slice(0, MAX_POPUPS)) {
        const { uri, diagnostic } = problem;
        const where = `${vscode.workspace.asRelativePath(uri)}:${diagnostic.range.start.line + 1}`;
        popup(isError(problem), `${TITLE}: ${diagnostic.message} (${where})`, 'Open',
            () => vscode.window.showTextDocument(uri, { selection: diagnostic.range }));
    }
    const others = problems.slice(MAX_POPUPS);
    if (others.length > 0) {
        popup(others.some(isError), `${TITLE}: ${others.length} more, ${problems.length} in all`, 'Show Problems',
            () => vscode.commands.executeCommand('workbench.actions.view.problems'));
    }
}

function report(exitCode) {
    reportProblems(exitCode);
    return reportWarnings(exitCode);
}

function activate(context) {
    let timer;
    context.subscriptions.push(
        vscode.tasks.onDidEndTaskProcess(event => {
            if (event.execution.task.name === TASK) {
                clearTimeout(timer);
                timer = setTimeout(report, WAIT_MS, event.exitCode);
            }
        }),
        { dispose: () => clearTimeout(timer) },
    );
}

module.exports = { activate };
