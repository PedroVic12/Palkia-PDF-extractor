// ==========================================
// API REST para Google Sheets
// ==========================================

// Configurações
const SHEET_NAME = 'SERVICOS'; // Nome da sua aba
const HEADERS_ROW = 1; // Linha dos cabeçalhos

// Função principal que recebe as requisições
function doGet(e) {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
    
    if (!sheet) {
      return createResponse({
        success: false,
        error: 'Planilha não encontrada'
      }, 404);
    }

    // Pega os dados
    const data = getSheetData(sheet);
    
    return createResponse({
      success: true,
      data: data,
      total: data.length
    });
    
  } catch (error) {
    return createResponse({
      success: false,
      error: error.toString()
    }, 500);
  }
}

function doPost(e) {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
    
    if (!sheet) {
      return createResponse({
        success: false,
        error: 'Planilha não encontrada'
      }, 404);
    }

    // Parse do JSON enviado
    const postData = JSON.parse(e.postData.contents);
    
    // Adiciona nova linha
    const newRow = addRowToSheet(sheet, postData);
    
    return createResponse({
      success: true,
      message: 'Dados adicionados com sucesso',
      data: newRow
    });
    
  } catch (error) {
    return createResponse({
      success: false,
      error: error.toString()
    }, 500);
  }
}

// Função para ler dados da planilha
function getSheetData(sheet) {
  const lastRow = sheet.getLastRow();
  
  if (lastRow < 2) {
    return []; // Sem dados além do cabeçalho
  }
  
  // Pega os cabeçalhos
  const headers = sheet.getRange(HEADERS_ROW, 1, 1, sheet.getLastColumn()).getValues()[0];
  
  // Pega todos os dados
  const data = sheet.getRange(2, 1, lastRow - 1, headers.length).getValues();
  
  // Converte array em objetos com os nomes das colunas
  return data.map(row => {
    const obj = {};
    headers.forEach((header, index) => {
      obj[header] = row[index];
    });
    return obj;
  });
}

// Função para adicionar nova linha
function addRowToSheet(sheet, data) {
  // Pega os cabeçalhos
  const headers = sheet.getRange(HEADERS_ROW, 1, 1, sheet.getLastColumn()).getValues()[0];
  
  // Cria array com os valores na ordem correta dos cabeçalhos
  const newRow = headers.map(header => data[header] || '');
  
  // Adiciona a nova linha
  sheet.appendRow(newRow);
  
  // Retorna o objeto criado
  const obj = {};
  headers.forEach((header, index) => {
    obj[header] = newRow[index];
  });
  
  return obj;
}

// Função para criar resposta JSON
function createResponse(data, statusCode = 200) {
  const response = ContentService.createTextOutput(JSON.stringify(data));
  response.setMimeType(ContentService.MimeType.JSON);
  
  return response;
}