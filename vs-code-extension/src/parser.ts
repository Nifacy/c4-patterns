import * as vscode from "vscode"


const PLUGIN_APPLY_EXPR = new RegExp(/(\$pattern\s+([a-z\.A-Z0-9]+)(?:\s*\{[\s\S]*?\})?)/g);
const PLUGIN_EXPR = new RegExp(/^\$pattern\s+(?<name>[a-z\.A-Z0-9]+)\s*(?:\{(?<params>[\s\S]*?)\})?$/gm);
const PARAM_EXPR = new RegExp(/^\s*(?<name>\S+)\s+(?<value>(?:['"][^'"\n]+['"])|\S+)\s*$/g);
const UNFINISHED_PARAM_EXPR = new RegExp(/^\s*(?<name>\S+)\s*$/g);
const STRING_BRACKETS_EXPR = new RegExp(/^['"]|['"]$/g);
const FIGURE_BRACKETS_EXPR = new RegExp(/^\{|\}$/g);


export interface ArrayArgumentName {
    array: string;
    index: number;
    field: string;
}


export type ArgumentName = string | ArrayArgumentName


export interface PluginArgument {
    name: ArgumentName;
    value: string;
}

export interface PluginApplyInfo {
    name: string;
    arguments: PluginArgument[];
    unfinishedArgumet?: string;
}


export function GetPluginApplyRanges(document: vscode.TextDocument): vscode.Range[] {
    const regex = new RegExp(PLUGIN_APPLY_EXPR);
    const text = document.getText();
    let matches;

    const ranges: vscode.Range[] = [];

    while ((matches = regex.exec(text)) !== null) {
        const startPos = document.positionAt(matches.index);
        const endPos = document.positionAt(matches.index + matches[0].length);
        const range = new vscode.Range(startPos, endPos);
        ranges.push(range);
    }

    return ranges;
}


function parsePluginArgumentName(s: string): ArgumentName {
    const parts = s.split(".");

    if (parts.length === 1) {
        return parts[0];
    }

    if (parts.length === 3) {
        const [array, indexStr, field] = parts;
        const index = parseInt(indexStr, 10);

        return {
            array: array,
            index: index,
            field: field,
        };
    }

    throw Error(`Can't parse argument name: '${s}'`)
}


function parsePluginArgument(s: string): PluginArgument {
    const matches = s.matchAll(PARAM_EXPR);

    for (let match of matches) {
        if (!match.groups) {
            throw Error("Unexpected empty group");
        }

        return {
            name: parsePluginArgumentName(match.groups.name),
            value: match.groups.value.replace(STRING_BRACKETS_EXPR, ""),
        }
    }

    throw Error(`Can't parse line: '${s}'`);
}


function parseUnfinishedPluginArgument(s: string): string {
    const matches = s.matchAll(UNFINISHED_PARAM_EXPR);

    for (let match of matches) {
        if (!match.groups) {
            throw Error("Unexpected empty group");
        }

        return match.groups.name;
    }

    throw Error(`Can't parse line: '${s}'`);
}


function splitByLines(text: string): string[] {
    let lines = text.replace(FIGURE_BRACKETS_EXPR, "").split(/\r?\n/);
    lines = lines.map(line => line.trim());
    lines = lines.filter(line => line !== "");
    return lines;
}


export function ParsePluginApplyInfo(text: string): PluginApplyInfo {
    const matches = text.matchAll(PLUGIN_EXPR);
    let pluginName: string | undefined = undefined;
    let pluginArgs: PluginArgument[] = [];
    let unfinishedArgument: string | undefined = undefined;

    for (let match of matches) {
        if (!match.groups) {
            throw Error("Unexpected empty group");
        }

        pluginName = match.groups.name.replace(STRING_BRACKETS_EXPR, "");

        if (match.groups?.params) {
            for (const line of splitByLines(match.groups.params)) {
                try {
                    const parsedArgument = parsePluginArgument(line);
                    pluginArgs.push(parsedArgument);
                } catch {
                    unfinishedArgument = parseUnfinishedPluginArgument(line);
                }
            }
        }

        return {
            name: pluginName,
            arguments: pluginArgs,
            unfinishedArgumet: unfinishedArgument,
        };
    }

    throw Error(`Can't parse script: '${text}'`);
}
