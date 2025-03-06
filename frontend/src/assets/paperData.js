export const paperMainLabels = {
  ticker: "Тикер",
  figi: "FIGI",
  isin: "ISIN",
  issue_size: "Размер выпуска",
  nominal: "Номинал",
  nominal_currency: "Валюта номинала",
  primary_index: "Основной индекс",
  preferred_share_type: "Тип привилегированных акций",
  ipo_date: "Дата IPO",
  registry_date: "Дата регистрации",
  issue_kind: "Вид выпуска",
  placement_date: "Дата размещения",
  repres_isin: "Представленный ISIN",
  issue_size_plan: "Плановый размер выпуска",
  total_float: "Общее количество в обращении",
};

export const issueKindMapping = {
  documentary: "документарный",
  non_documentary: "недокументарный",
};
/////////////////////////////////

export const divsLabels = {
  dividend_net: "Дивиденд",
  payment_date: "Дата фактической выплаты",
  declared_date: "Дата объявления дивидендов",
  last_buy_date: "Последний день покупки",
  dividend_type: "Тип выплаты",
  record_date: "Дата фиксации реестра",
  regularity: "Регулярность выплаты",
  close_price: "Цена закрытия",
  yield_value: "Доходность",
  created_at: "Дата создания записи",

  five_years_average_dividend_yield: "Средн. див. доходность за 5 лет",
  dividend_payout_ratio_fy: "Коэффициент выплаты дивидендов",
  forward_annual_dividend_yield: "Прогнозируемая див. доходность",
};

export const regilarityMapping = {
  Annual: "Ежегодная",
  "Semi-anl": "Каждые полгода",
  Quarter: "Квартальная",
};

export const multiplicatorsLabels = {
  market_capitalization: "Рыночная капитализация",
  ticker: "Тикер",
  currency: "Валюта",
  high_price_last_52_weeks: "Макс. цена за 52 недели",
  low_price_last_52_weeks: "Мин. цена за 52 недели",
  average_daily_volume_last_10_days: "Средний объем за 10 дней",
  average_daily_volume_last_4_weeks: "Средний объем за 4 недели",
  beta: "Бета",
  free_float: "Free float",
  shares_outstanding: "Акций в обращении",
  revenue_ttm: "Выручка (TTM)",
  ebitda_ttm: "EBITDA (TTM)",
  net_income_ttm: "Чистая прибыль (TTM)",
  eps_ttm: "Прибыль на акцию (EPS TTM)",
  pe_ratio_ttm: "P/E",
  price_to_sales_ttm: "P/S",
  price_to_book_ttm: "P/B",
  total_enterprise_value_mrq: "Стоимость предприятия (EV)",
  ev_to_ebitda_mrq: "EV/EBITDA",
  roe: "ROE",
  roa: "ROA",
  roic: "ROIC",
  total_debt_to_equity_mrq: "Долг/Собственный капитал",
  total_debt_to_ebitda_mrq: "Долг/EBITDA",
  current_ratio_mrq: "Текущая ликвидность",
  buy_back_ttm: "Обратный выкуп (TTM)",
  one_year_annual_revenue_growth_rate: "Рост выручки за 1 год",
  revenue_change_five_years: "Изменение выручки за 5 лет",
  eps_change_five_years: "Изменение EPS за 5 лет",
  ev_to_sales: "EV/Sales",
  ex_dividend_date: "Дата закрытия реестра",
};

export const metricGroups = {
  general: ["market_capitalization", "ticker", "currency", "shares_outstanding"],
  pricing: ["high_price_last_52_weeks", "low_price_last_52_weeks", "beta"],
  tradingActivity: ["average_daily_volume_last_10_days", "average_daily_volume_last_4_weeks", "free_float", "buy_back_ttm"],
  financialPerformance: ["revenue_ttm", "ebitda_ttm", "net_income_ttm", "eps_ttm"],
  valuationRatios: ["pe_ratio_ttm", "price_to_sales_ttm", "price_to_book_ttm", "ev_to_ebitda_mrq", "ev_to_sales"],
  profitability: ["roe", "roa", "roic"],
  debt: ["total_debt_to_equity_mrq", "total_debt_to_ebitda_mrq", "current_ratio_mrq", "total_enterprise_value_mrq"],
  growth: ["one_year_annual_revenue_growth_rate", "revenue_change_five_years", "eps_change_five_years"],
};

export const groupHeaders = {
  general: "Общая информация",
  pricing: "Цены акций",
  tradingActivity: "Торговая активность",
  financialPerformance: "Финансовые показатели",
  valuationRatios: "Коэффициенты оценки",
  profitability: "Рентабельность",
  debt: "Долг и ликвидность",
  growth: "Рост",
};

export const sectorsLabels = {
  tech: "Технологии и IT",
  retail: "Розничная торговля",
  banks: "Банки и финансы",
  build: "Строительство и девелопмент",
  oil: "Нефть и газ",
};

export const companyNames = {
  // tech
  YDEX: "Яндекс",
  HEAD: "HeadHunter",
  VKCO: "VK",
  ASTR: "АстраЛинукс",

  // retail
  MGNT: "Магнит",
  OZON: "Озон",
  LENT: "Лента",
  X5: "X5 Retail Group",
  OKEY: "О'Кей",

  // banks
  SBER: "Сбер",
  TCS: "T-банк",
  SVCB: "Совкомбанк",
  VTBR: "ВТБ",
  CBOM: "МКБ",

  // build
  SMLT: "Самолет",
  PIKK: "ПИК",
  LSRG: "ЛСР",
  MSTT: "Мостотрест",

  // oil
  GAZP: "Газпром",
  ROSN: "Роснефть",
  LKOH: "Лукойл",
  NVTK: "НОВАТЭК",
  TATN: "Татнефть",
};
