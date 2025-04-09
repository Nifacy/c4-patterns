import { spawn } from "child_process";


export interface SingleField {
    name: string;
    optional: true;
}


export interface ArrayField {
    name: string;
    fields: Field[];
}


export type Field = SingleField | ArrayField;


export interface PatternInfo {
    pluginName: string;
    docs: string;
    params: Field[];
}


export class PatternLensError extends Error {
    constructor(args: string[], code: number | null) {
        const command = args.join(" ");
        super(`Pattern Lens command '${command}' failed with code ${code}`);
    }
}


class Logger {
    private prefix: string;

    constructor(prefix: string | undefined = undefined) {
        this.prefix = (prefix !== undefined) ? prefix : "";
    }

    public static Extend(prefix: string, sourceLogger: Logger): Logger {
        return new Logger(sourceLogger.prefix + ` ${prefix}`);
    }

    public log(message: string): void {
        console.log(this.prefix + " " + message);
    }

    public error(message: string): void {
        console.error(this.prefix + " " + message);
    }
}


export class PatternLens {
    private jarPath: string;
    private logger: Logger;

    constructor(jarPath: string) {
        this.jarPath = jarPath;
        this.logger = new Logger("[PatternLens]");
    }

    public async IsPattern(workspacePath: string, pluginName: string): Promise<boolean> {
        const methodLogger = Logger.Extend("[IsPattern]", this.logger);

        methodLogger.log(`workspacePath: '${workspacePath}', pluginName: '${pluginName}'`);
        const output = await this.runJar(methodLogger, "is-pattern", workspacePath, pluginName);
        methodLogger.log(`output: '${output}'`)
        const result = output === "true";
        methodLogger.log(`pluginName: '${pluginName}', result: ${result}`);
        return result;
    }

    public async GetInfo(workspacePath: string, pluginName: string): Promise<PatternInfo> {
        const methodLogger = Logger.Extend("[GetParams]", this.logger);
        methodLogger.log(`workspacePath: '${workspacePath}', pluginName: '${pluginName}'`);

        const output = await this.runJar(methodLogger, "info", workspacePath, pluginName);
        methodLogger.log(`output: '${output}'`);

        return JSON.parse(output) as PatternInfo;
    }

    private async runJar(logger: Logger, command: string, ...args: string[]): Promise<string> {
        const localLogger = Logger.Extend("[runJar]", logger);

        return new Promise((resolve, reject) => {
            localLogger.log(`run: '${command} ${args.join(" ")}'`)

            const javaProcess = spawn("java", ["-Dfile.encoding=UTF-8", "-jar", this.jarPath, command, ...args]);
            javaProcess.stdout.setEncoding("utf-8");
            javaProcess.stderr.setEncoding("utf-8");

            let stdout = "";

            javaProcess.stdout.on("data", data => {
                localLogger.log(`Data: '${typeof(data)}'`);
                stdout += data.toString();
            });

            javaProcess.stderr.on("data", data => {
                console.log("[PatternLens] " + data.toString());
            });

            javaProcess.on("close", code => {
                if (code !== 0) {
                    reject(new PatternLensError(
                        [command, ...args],
                        code,
                    ));
                } else {
                    resolve(stdout.trim());
                }
            });
        });
    }
}
