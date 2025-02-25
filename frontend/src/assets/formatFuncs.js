export const formatValue = (value) => {
  if (typeof value === "number") {
    return new Intl.NumberFormat("ru-RU").format(value);
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
