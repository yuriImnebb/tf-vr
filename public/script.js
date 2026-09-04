const botao = document.getElementById("continuar");

botao.addEventListener("click", async () => {

    const nome = document.getElementById("nome").value;
    const senha = document.getElementById("senha").value;

    if (!nome || !senha) {
        alert("Preencha todos os campos.");
        return;
    }

    try {

        const resposta = await fetch("/salvar", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                nome: nome,
                senha: senha
            })
        });

        const resultado = await resposta.json();

        if (resultado.success) {
            alert("Salvo!");
        } else {
            alert("Erro ao salvar.");
        }

    } catch (erro) {
        console.error(erro);
        alert("Erro ao conectar com o servidor.");
    }

});