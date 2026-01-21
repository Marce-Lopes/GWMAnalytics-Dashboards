# Relatório de Bolso GWM - Documentação de Negócios

## Visão Geral
Este painel fornece um panorama em tempo real do desempenho de vendas dos veículos GWM (H6, ORA, etc.). Projetado para uso móvel ("Pocket Report"), ele monitora indicadores-chave de desempenho (KPIs) como pedidos pagos, pedidos não pagos e atividades recentes.

## Fontes de Dados
- **Banco de Dados**: ClickHouse (`mart.ecommerce_pocket_report`)
- **Frequência de Atualização**: Tempo real (Consulta direta ao banco de dados)

## Definições das Métricas Chave

### 1. Formulário 9k Com Pagamento (Pago)
- **Definição**: Pedidos confirmados onde o pagamento foi processado.
- **Filtro**: `Status = 'Invoiced'`
- **Escopo Temporal**:
    - **Mês Atual**: Todos os pedidos faturados até ontem (`Data < Hoje - 1`).
    - **Meses Anteriores**: Todos os pedidos faturados naquele mês.

### 2. Formulário 9k Sem Pagamento (Não Pago)
- **Definição**: Pedidos que estão abertos ou ainda não faturados.
- **Filtro**: `Status` é `'Not Invoiced'` ou `'Open'`.
- **Escopo Temporal**:
    - **Mês Atual**: Todos os pedidos abertos/não faturados até ontem (`Data < Hoje - 1`).
    - **Meses Anteriores**: Todos os pedidos abertos/não faturados naquele mês.

### 3. Últimas 24 Horas (Atividade Recente)
- **Definição**: Todos os pedidos realizados desde ontem. Isso captura a atividade mais recente do mercado.
- **Filtro**: `Data >= Hoje - 1`
- **Nota**: Esta métrica inclui *todos* os status para mostrar o fluxo total recente.
- **Exibição**: Mostrado separadamente no resumo e mesclado nos gráficos do mês atual.

### 4. Total
- **Definição**: A soma de Pagos + Não Pagos + Últimas 24h (para a visualização do mês atual).

## Dimensões e Detalhamento
O painel detalha essas métricas por:
- **Família de Veículos**: Modelos específicos (ex: H6 HEV2, H6 GT).
- **Cor Exterior**: Distribuição de vendas por cor do carro.
- **Evolução Diária**: Linha de tendência dos pedidos ao longo do mês.
- **Estado do Revendedor**: Distribuição geográfica das vendas.
- **Grupo de Revendedores**: Desempenho por grupos de rede de concessionárias.

## Análise Comparativa
- Permite comparar tendências diárias entre diferentes veículos ou meses.
- Suporta filtragem por "Com Pagamento", "Sem Pagamento" ou "Total".
