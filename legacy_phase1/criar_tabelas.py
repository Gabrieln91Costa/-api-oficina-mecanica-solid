from sqlalchemy import inspect
from sqlalchemy import text
from sqlmodel import SQLModel

from core.database import engine


async def create_tables() -> None:

    # ==========================================================
    # IMPORTA TODOS OS MODELS
    # ==========================================================

    import models.__all_models

    print("=" * 60)
    print("INICIANDO CRIAÇÃO / ATUALIZAÇÃO DO BANCO DE DADOS")
    print("=" * 60)

    try:

        async with engine.begin() as conn:

            print("\n[BANCO] Verificando banco SQLite...")
            print("[OK] Banco SQLite disponível.")

            # ======================================================
            # TABELAS DO SQLMODEL
            # ======================================================

            tables = list(
                SQLModel.metadata.sorted_tables
            )

            if not tables:

                print(
                    "\n[AVISO] Nenhuma tabela encontrada."
                )

                return

            # ======================================================
            # INSPECT
            # ======================================================

            existing_tables = await conn.run_sync(
                lambda sync_conn: inspect(
                    sync_conn
                ).get_table_names()
            )

            criadas = []
            atualizadas = []
            existentes = []
            erros = []

            # ======================================================
            # PROCESSA CADA TABELA
            # ======================================================

            for table in tables:

                nome_tabela = table.name

                # ==================================================
                # TABELA NÃO EXISTE
                # ==================================================

                if nome_tabela not in existing_tables:

                    print(
                        f"\n[CRIANDO] {nome_tabela}..."
                    )

                    try:

                        await conn.run_sync(
                            lambda sync_conn, t=table:
                            t.create(
                                sync_conn,
                                checkfirst=True
                            )
                        )

                        print(
                            f"[OK] {nome_tabela} criada."
                        )

                        criadas.append(
                            nome_tabela
                        )

                    except Exception as error:

                        print(
                            f"[ERRO] Falha ao criar "
                            f"{nome_tabela}"
                        )

                        print(
                            f"[ERRO] Motivo: {error}"
                        )

                        erros.append(
                            {
                                "tabela": nome_tabela,
                                "erro": str(error)
                            }
                        )

                    continue

                # ==================================================
                # TABELA JÁ EXISTE
                # ==================================================

                print(
                    f"\n[EXISTENTE] {nome_tabela}"
                )

                existentes.append(
                    nome_tabela
                )

                # ==================================================
                # COLUNAS EXISTENTES
                # ==================================================

                existing_columns = await conn.run_sync(
                    lambda sync_conn, tn=nome_tabela:
                    inspect(
                        sync_conn
                    ).get_columns(tn)
                )

                existing_column_names = {
                    column["name"]
                    for column in existing_columns
                }

                # ==================================================
                # VERIFICA NOVAS COLUNAS
                # ==================================================

                novas_colunas = []

                for column in table.columns:

                    if column.name not in existing_column_names:

                        novas_colunas.append(
                            column
                        )

                # ==================================================
                # ADICIONA NOVAS COLUNAS
                # ==================================================

                if novas_colunas:

                    print(
                        f"[ATUALIZANDO] {nome_tabela}"
                    )

                    for column in novas_colunas:

                        try:

                            column_type = column.type.compile(
                                dialect=conn.dialect
                            )

                            sql = (
                                f'ALTER TABLE "{nome_tabela}" '
                                f'ADD COLUMN "{column.name}" '
                                f'{column_type}'
                            )

                            # --------------------------------------
                            # DEFAULT
                            # --------------------------------------

                            if column.default is not None:

                                try:

                                    default_value = (
                                        column.default.arg
                                    )

                                    if isinstance(
                                        default_value,
                                        str
                                    ):

                                        sql += (
                                            f" DEFAULT "
                                            f"'{default_value}'"
                                        )

                                    elif isinstance(
                                        default_value,
                                        bool
                                    ):

                                        sql += (
                                            f" DEFAULT "
                                            f"{1 if default_value else 0}"
                                        )

                                    else:

                                        sql += (
                                            f" DEFAULT "
                                            f"{default_value}"
                                        )

                                except Exception:

                                    pass

                            # --------------------------------------
                            # NULLABLE
                            # --------------------------------------

                            if not column.nullable:

                                print(
                                    f"[AVISO] Coluna "
                                    f"{column.name} "
                                    f"é NOT NULL."
                                )

                                print(
                                    "[AVISO] SQLite pode exigir "
                                    "tratamento manual se a tabela "
                                    "já possuir registros."
                                )

                            print(
                                f"  [ADICIONANDO] "
                                f"{column.name} "
                                f"({column_type})"
                            )

                            await conn.execute(
                                text(sql)
                            )

                            print(
                                f"  [OK] Coluna "
                                f"{column.name} adicionada."
                            )

                            atualizadas.append(
                                f"{nome_tabela}.{column.name}"
                            )

                        except Exception as error:

                            print(
                                f"  [ERRO] Não foi possível "
                                f"adicionar "
                                f"{column.name}"
                            )

                            print(
                                f"  [ERRO] Motivo: {error}"
                            )

                            erros.append(
                                {
                                    "tabela": nome_tabela,
                                    "coluna": column.name,
                                    "erro": str(error)
                                }
                            )

                else:

                    print(
                        f"[OK] {nome_tabela} "
                        f"já está atualizada."
                    )

            # ======================================================
            # RESUMO
            # ======================================================

            print("\n" + "=" * 60)
            print("RESUMO")
            print("=" * 60)

            print(
                f"[OK] Tabelas criadas: "
                f"{len(criadas)}"
            )

            print(
                f"[INFO] Tabelas existentes: "
                f"{len(existentes)}"
            )

            print(
                f"[UPDATE] Colunas adicionadas: "
                f"{len(atualizadas)}"
            )

            print(
                f"[ERRO] Erros: "
                f"{len(erros)}"
            )

            # ======================================================
            # DETALHES DAS ALTERAÇÕES
            # ======================================================

            if atualizadas:

                print(
                    "\nCOLUNAS ADICIONADAS:"
                )

                for coluna in atualizadas:

                    print(
                        f"  - {coluna}"
                    )

            # ======================================================
            # DETALHES DOS ERROS
            # ======================================================

            if erros:

                print(
                    "\nDETALHES DOS ERROS:"
                )

                for erro in erros:

                    if "coluna" in erro:

                        print(
                            f"  - {erro['tabela']}."
                            f"{erro['coluna']}: "
                            f"{erro['erro']}"
                        )

                    else:

                        print(
                            f"  - {erro['tabela']}: "
                            f"{erro['erro']}"
                        )

                raise RuntimeError(
                    "Uma ou mais alterações "
                    "não puderam ser realizadas."
                )

    except Exception as error:

        print("\n" + "=" * 60)
        print("ERRO NA INICIALIZAÇÃO DO BANCO")
        print("=" * 60)

        print(
            f"Motivo: {error}"
        )

        raise

    else:

        print("\n" + "=" * 60)
        print(
            "BANCO DE DADOS "
            "INICIALIZADO / ATUALIZADO COM SUCESSO!"
        )
        print("=" * 60)


# ==========================================================
# EXECUÇÃO
# ==========================================================

if __name__ == "__main__":

    import asyncio

    asyncio.run(
        create_tables()
    )