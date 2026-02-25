import * as vscode from 'vscode';
import { exec } from 'child_process';

export function activate(context: vscode.ExtensionContext) {
    const outputChannel = vscode.window.createOutputChannel('CheckodAI');
    context.subscriptions.push(outputChannel);

    let disposable = vscode.commands.registerCommand('checkod-ai.assess', () => {
        outputChannel.clear();
        exec('checkod assess', (error, stdout) => {
            if (error) {
                outputChannel.appendLine(error.message);
                outputChannel.show(true);
                return;
            }

            outputChannel.append(stdout);
            outputChannel.show(true);
        });
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {}
