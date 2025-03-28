export const formatValue = (value, decimals = 2) => {
  if (value === null || value === undefined || value === "") {
    return "";
  }

  const numValue = typeof value === "string" ? parseFloat(value) : value;

  if (!isNaN(numValue)) {
    // Форматирование по ru-RU даёт разделитель тысяч как пробел, а десятичный знак - запятая.
    // Заменяем запятую на точку.
    return new Intl.NumberFormat("ru-RU", {
      minimumFractionDigits: 0,
      maximumFractionDigits: decimals,
    })
      .format(numValue)
      .replace(",", ".");
  }

  return value;
};

export const formatDate = (dateStr) => {
  const date = new Date(dateStr);
  const day = String(date.getDate()).padStart(2, "0");
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const year = date.getFullYear();
  return `${day}.${month}.${year}`;
};

export const formatValueFixed = (value, decimals = 2) => {
  if (value === null || value === undefined || value === "") {
    return "";
  }
  const numValue = typeof value === "string" ? parseFloat(value) : value;
  return isNaN(numValue) ? value : numValue.toFixed(decimals);
};
