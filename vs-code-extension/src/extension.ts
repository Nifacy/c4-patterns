import * as vscode from "vscode";
import * as fs from "fs"

import * as pluginParser from "./parser";
import * as lens from "./patternLens";


interface PatternApplyInfo {
	range: vscode.Range;
	pluginApplyInfo: pluginParser.PluginApplyInfo;
	patternInfo: lens.PatternInfo;
};


interface UnpackedParameter {
	argumentName: pluginParser.ArgumentName;
	optional: boolean;
};


async function openFileInNewTab(filePath: string): Promise<void> {
	if (!fs.existsSync(filePath)) {
		throw Error(`The file ${filePath} does not exist.`)
	}

	const openedDocument = await vscode.workspace.openTextDocument(filePath);
	await vscode.window.showTextDocument(openedDocument, vscode.ViewColumn.One);
}


async function getPatternApply(
	patternLens: lens.PatternLens,
	document: vscode.TextDocument,
	applyRange: vscode.Range
): Promise<PatternApplyInfo | undefined> {
	const workspaceFilePath = document.fileName;
	const rawPluginApplyText = document.getText(applyRange);
	const pluginApplyInfo = pluginParser.ParsePluginApplyInfo(rawPluginApplyText);

	const isPattern = await patternLens.IsPattern(workspaceFilePath, pluginApplyInfo.name);
	if (!isPattern) {
		return undefined;
	}

	return {
		range: applyRange,
		pluginApplyInfo: pluginApplyInfo,
		patternInfo: await patternLens.GetInfo(workspaceFilePath, pluginApplyInfo.name),
	};
}


function getDefinedIndexes(name: string, argNames: pluginParser.ArgumentName[]): number[] {
	const definedIndexes: number[] = [];

	for (const argName of argNames) {
		if (typeof argName === "string") {
			continue;
		}

		if (argName.array === name) {
			if (!definedIndexes.includes(argName.index)) {
				definedIndexes.push(argName.index);
			}
		}
	}

	return definedIndexes;
}


function unpackParams(
	params: lens.Field[],
	args: pluginParser.ArgumentName[]
): UnpackedParameter[] {
	const result: UnpackedParameter[] = [];

	for (const param of params) {
		if ((param as lens.SingleField).optional !== undefined) {
			const singledField = param as lens.SingleField;

			result.push({
				argumentName: singledField.name,
				optional: singledField.optional,
			});
			continue;
		}

		const fieldGroup = param as lens.ArrayField;
		for (const index of getDefinedIndexes(fieldGroup.name, args)) {
			for (const field of fieldGroup.fields) {
				result.push({
					argumentName: {
						array: param.name,
						index: index,
						field: field.name,
					},
					optional: (field as lens.SingleField).optional,
				});
			}
		}
	}

	return result;
}


function dumpPluginArgumentName(name: pluginParser.ArgumentName): string {
	if (typeof name === "string") {
		return name;
	}
	return `${name.array}.${name.index}.${name.field}`;
}


class HoverProvider implements vscode.HoverProvider {
	private patternLens: lens.PatternLens;

	constructor(patternLens: lens.PatternLens) {
		this.patternLens = patternLens;
	}

	provideHover(
		document: vscode.TextDocument,
		position: vscode.Position,
		token: vscode.CancellationToken
	): vscode.ProviderResult<vscode.Hover> {
		return this.asyncProvideHover(document, position);
	}

	private async asyncProvideHover(
		document: vscode.TextDocument,
		position: vscode.Position,
	): Promise<vscode.Hover | undefined> {
		for (const applyRange of pluginParser.GetPluginApplyRanges(document)) {
			if (!applyRange.contains(position)) {
				continue;
			}

			try {
				const info = await getPatternApply(this.patternLens, document, applyRange);
				if (info?.patternInfo.docs === undefined) {
					continue;
				}

				const markdownContent = new vscode.MarkdownString(info.patternInfo.docs);
				return new vscode.Hover(markdownContent, info.range);
			} catch (e) {
				console.log(`Got error: ${e}`);
			}
		}

		return undefined;
	}
}


class CompletionProvider implements vscode.CompletionItemProvider {
	private patternLens: lens.PatternLens;

	constructor(patternLens: lens.PatternLens) {
		this.patternLens = patternLens;
	}

	provideCompletionItems(
		document: vscode.TextDocument,
		position: vscode.Position,
		token: vscode.CancellationToken,
		context: vscode.CompletionContext,
	): vscode.ProviderResult<vscode.CompletionItem[]> {
		return this.asyncProvideCompletionItems(document, position);
	}

	private async asyncProvideCompletionItems(
		document: vscode.TextDocument,
		position: vscode.Position,
	): Promise<vscode.CompletionItem[] | undefined> {
		console.log("Completion Provider called");

		for (const applyRange of pluginParser.GetPluginApplyRanges(document)) {
			if (!applyRange.contains(position)) {
				continue;
			}

			const info = await getPatternApply(this.patternLens, document, applyRange);
			if (info === undefined) {
				continue;
			}

			if (info.pluginApplyInfo.unfinishedArgumet !== undefined) {
				const arg = info.pluginApplyInfo.unfinishedArgumet;

				const args = (info.pluginApplyInfo.arguments ?? []).map(arg => arg.name);
				const params = info.patternInfo.params ?? [];
				const totalArgs = unpackParams(params, args).map(p => p.argumentName);

				const dumpedArgs = args.map(dumpPluginArgumentName);
				const dumpedRequiredArgs = totalArgs.map(dumpPluginArgumentName);

				const missingParams = dumpedRequiredArgs.filter(arg => !dumpedArgs.includes(arg));
				const suggestedParams = missingParams.filter(param => param.startsWith(arg));

				return suggestedParams.map(
					param => new vscode.CompletionItem(
						param,
						vscode.CompletionItemKind.Issue,
					)
				);
			}
		}

		return undefined;
	}
}


function createRequiredArgumentError(
	document: vscode.TextDocument,
	patternApplyInfo: PatternApplyInfo,
	extraArgument: string,
): vscode.Diagnostic {
	const pluginText = document.getText(patternApplyInfo.range);
	const pluginOffset = document.offsetAt(patternApplyInfo.range.start);

	const startIndex = pluginText.indexOf(extraArgument);
	const endIndex = startIndex + extraArgument.length;

	const startPosition = document.positionAt(pluginOffset + startIndex);
	const endPosition = document.positionAt(pluginOffset + endIndex);

	return {
		message: `Extra argument '${extraArgument}'`,
		range: new vscode.Range(startPosition, endPosition),
		severity: vscode.DiagnosticSeverity.Error,
	};
}


function createMissingParameterError(
	document: vscode.TextDocument,
	patternApplyInfo: PatternApplyInfo,
	missingParameter: string,
): vscode.Diagnostic {
	const pluginOffset = document.offsetAt(patternApplyInfo.range.start);
	const pluginText = document.getText(patternApplyInfo.range);

	const startHeaderPosition = document.positionAt(pluginOffset);
	const endHeaderPosition = document.positionAt(pluginOffset + pluginText.indexOf(" "));

	const headerRange = new vscode.Range(startHeaderPosition, endHeaderPosition);

	return {
		message: `Parameter '${missingParameter}' is required`,
		range: headerRange,
		severity: vscode.DiagnosticSeverity.Error,
	};
}


function checkArgumentsSet(
	document: vscode.TextDocument,
	patternApplyInfo: PatternApplyInfo,
): vscode.Diagnostic[] {
	const diagnostics: vscode.Diagnostic[] = [];

	for (const arg of patternApplyInfo.pluginApplyInfo.arguments) {
		console.log(`- ${arg.name}`);
	}

	const args = patternApplyInfo.pluginApplyInfo.arguments ?? [];
	const argNames = args.map(arg => arg.name);
	const params = patternApplyInfo.patternInfo.params ?? [];

	const unpackedParams = unpackParams(params, argNames);
	const requiredArgs = unpackedParams.filter(p => !p.optional).map(p => p.argumentName);
	const totalArgs = unpackedParams.map(p => p.argumentName);

	console.log("required args:")
	console.log(requiredArgs);

	console.log("total args:");
	console.log(totalArgs);

	const dumpedArgNames = argNames.map(dumpPluginArgumentName);
	const dumpedRequiredArgs = requiredArgs.map(dumpPluginArgumentName);
	const dumpedTotalArgs = totalArgs.map(dumpPluginArgumentName);

	const extraArgs = dumpedArgNames.filter(arg => !dumpedTotalArgs.includes(arg));
	const missingArguments = dumpedRequiredArgs.filter(arg => !dumpedArgNames.includes(arg));

	for (const extraArg of extraArgs) {
		diagnostics.push(createRequiredArgumentError(document, patternApplyInfo, extraArg));
	}

	for (const missingParam of missingArguments) {
		diagnostics.push(createMissingParameterError(document, patternApplyInfo, missingParam));
	}

	return diagnostics;
}


async function updateDiagnostics(
	patternLens: lens.PatternLens,
	document: vscode.TextDocument,
	collection: vscode.DiagnosticCollection,
): Promise<void> {
	const argumentsCheckDiagnostics: vscode.Diagnostic[] = [];

	for (const applyRange of pluginParser.GetPluginApplyRanges(document)) {
		try {
			const info = await getPatternApply(patternLens, document, applyRange);
			if (info === undefined) {
				continue;
			}

			for (const diagnostic of checkArgumentsSet(document, info)) {
				argumentsCheckDiagnostics.push(diagnostic);
			}
		} catch (e) {
			console.error(`Got error: ${e}`);
		}
	}

	collection.clear();
	collection.set(document.uri, argumentsCheckDiagnostics);
}


export async function activate(context: vscode.ExtensionContext) {
	try {
		console.log("Activate ...");

		const extensionConfig = vscode.workspace.getConfiguration("c4dslpatterns");

		console.log("Initialize Pattern Lens client...");

		const patternLensPath = extensionConfig.get("patternLensPath") as (string | undefined);
		if (patternLensPath === undefined) {
			throw Error("Pattern Lens jar file not defined");
		}

		if (!fs.existsSync(patternLensPath)) {
			throw Error(`Pattern Lens jar file '${patternLensPath}' doesn't exist`);
		}

		const patternLensClient = new lens.PatternLens(patternLensPath);

		console.log("Initialize Pattern Lens client... [ok]");

		console.log("Register Hover provider ...");

		vscode.languages.registerHoverProvider(
			"*",
			new HoverProvider(patternLensClient),
		);

		console.log("Register Hover provider ... [ok]");

		console.log("Register commands ...");

		vscode.commands.registerCommand(
			"structurizr-templates.showPluginDefinition",
			(pluginName: string) => openFileInNewTab(pluginName),
		);

		console.log("Register commands ... [ok]")

		console.log("Register diagnostics ...");

		const collection = vscode.languages.createDiagnosticCollection("structurizr-templates.diagnostics");

		if (vscode.window.activeTextEditor) {
			updateDiagnostics(patternLensClient, vscode.window.activeTextEditor.document, collection);
		}

		context.subscriptions.push(
			vscode.workspace.onDidSaveTextDocument(document => {
				updateDiagnostics(patternLensClient, document, collection);
			})
		);

		console.log("Register diagnostics ... [ok]");

		console.log("Register completion provider ...");

		context.subscriptions.push(
			vscode.languages.registerCompletionItemProvider(
				"*",
				new CompletionProvider(patternLensClient),
			)
		);

		console.log("Register completion provider ... [ok]");

		console.log("Activate ... [ok]");
	} catch (e) {
		console.error(`[error] ${e}`);
	}
}

export function deactivate() {
	console.log("Deactivate ...");
	console.log("Deactivate ... [ok]");
}
