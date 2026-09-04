const express = require("express");
const fs = require("fs");
const path = require("path");
const { execFile } = require("child_process");

const app = express();

const PORT = 3000;


const PUBLIC_DIR = path.join(__dirname, "public");

const DADOS_JSON = path.join(
    __dirname,
    "dados.json"
);

const RESULTADO_JSON = path.join(
    __dirname,
    "resultado.json"
);

const BOT_PY = path.join(
    __dirname,
    "bot.py"
);


const PYTHON = "python";


app.use(
    express.json()
);

app.use(
    express.static(PUBLIC_DIR)
);


function lerDados() {

    if (!fs.existsSync(DADOS_JSON)) {
        return [];
    }

    try {

        const conteudo = fs.readFileSync(
            DADOS_JSON,
            "utf8"
        );

        if (!conteudo.trim()) {
            return [];
        }

        const dados = JSON.parse(conteudo);

        if (Array.isArray(dados)) {
            return dados;
        }

        return [];

    } catch (erro) {

        console.error(
            "Erro ao ler dados.json:",
            erro
        );

        return [];
    }
}



function lerResultados() {

    if (!fs.existsSync(RESULTADO_JSON)) {
        return [];
    }

    try {

        const conteudo = fs.readFileSync(
            RESULTADO_JSON,
            "utf8"
        );

        if (!conteudo.trim()) {
            return [];
        }

        const resultados = JSON.parse(conteudo);


        if (Array.isArray(resultados)) {
            return resultados;
        }



        if (
            resultados &&
            typeof resultados === "object"
        ) {
            return [resultados];
        }


        return [];

    } catch (erro) {

        console.error(
            "Erro ao ler resultado.json:",
            erro
        );

        return [];
    }
}



function executarBot() {

    return new Promise(
        (resolve, reject) => {

            execFile(
                PYTHON,
                [BOT_PY],

                {
                    cwd: __dirname,
                    timeout: 60000
                },

                (erro, stdout, stderr) => {

                    if (stdout) {

                        console.log(
                            "\n========== BOT =========="
                        );

                        console.log(stdout);

                        console.log(
                            "=========================\n"
                        );
                    }


                    if (stderr) {

                        console.error(
                            "\n========== PYTHON STDERR =========="
                        );

                        console.error(stderr);

                        console.error(
                            "===================================\n"
                        );
                    }


                    if (erro) {

                        reject(erro);
                        return;
                    }


                    resolve();
                }
            );
        }
    );
}



app.post(
    "/salvar",

    async (req, res) => {

        const {
            nome,
            senha
        } = req.body;



        if (
            typeof nome !== "string" ||
            typeof senha !== "string" ||
            !nome.trim() ||
            !senha
        ) {

            return res.status(400).json({
                success: false,
                status: "erro",
                mensagem: "Preencha todos os campos."
            });
        }


        try {

    
            const resultadosAntes =
                lerResultados();

            const quantidadeAntes =
                resultadosAntes.length;


            const dados = lerDados();


            dados.push({
                nome: nome.trim(),
                senha: senha
            });


            fs.writeFileSync(
                DADOS_JSON,
                JSON.stringify(
                    dados,
                    null,
                    4
                ),
                "utf8"
            );


            console.log(
                `Nova tentativa: ${nome.trim()}`
            );


     
            console.log(
                "Executando bot.py..."
            );


            await executarBot();


            const resultadosDepois =
                lerResultados();


            if (
                resultadosDepois.length <=
                quantidadeAntes
            ) {

                console.error(
                    "bot.py terminou, mas não criou um novo log."
                );


                return res.status(500).json({
                    success: false,
                    status: "erro",
                    mensagem:
                        "Não foi possível obter o resultado da verificação."
                });
            }


            const ultimoResultado =
                resultadosDepois[
                    resultadosDepois.length - 1
                ];


            console.log(
                "Resultado:",
                ultimoResultado.valido
                    ? "VÁLIDO"
                    : "INVÁLIDO"
            );


          
            if (
                ultimoResultado.valido === true
            ) {

                return res.json({
                    success: true,

                    status: "codigo",

                    mensagem:
                        "Login válido. Código necessário."
                });
            }


           
            return res.status(401).json({
                success: false,

                status: "invalido",

                mensagem:
                    "Nome ou senha inválidos."
            });


        } catch (erro) {

            console.error(
                "Erro em /salvar:",
                erro
            );


            return res.status(500).json({
                success: false,

                status: "erro",

                mensagem:
                    "Erro interno durante a verificação."
            });
        }
    }
);


app.get(
    "/",
    (req, res) => {

        res.sendFile(
            path.join(
                PUBLIC_DIR,
                "index.html"
            )
        );
    }
);



app.listen(
    PORT,
    () => {

        console.log();
        console.log(
            "===================================="
        );

        console.log(
            `Servidor rodando em http://localhost:${PORT}`
        );

        console.log(
            "===================================="
        );

        console.log();
    }
);