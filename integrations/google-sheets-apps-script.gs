/**
 * קליטת לידים מדף הנחיתה ל-Google Sheets
 *
 * הוראות:
 * 1. פותחים Google Sheet חדש → Extensions → Apps Script
 * 2. מדביקים את כל הקובץ הזה במקום הקוד הקיים ושומרים
 * 3. Deploy → New deployment → Type: Web app
 *    Execute as: Me | Who has access: Anyone
 * 4. מעתיקים את ה-Web app URL ומדביקים ב-index.html בשדה LP_CONFIG.webhookUrl
 * 5. (אופציונלי) ממלאים NOTIFY_EMAIL כדי לקבל מייל על כל ליד חדש
 */

const SHEET_NAME = 'Leads';
const NOTIFY_EMAIL = ''; // למשל 'office@example.com'

const COLUMNS = [
  'submitted_at', 'name', 'phone', 'email', 'years', 'practice', 'consent',
  'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'fbclid',
  'page', 'referrer', 'event_id'
];

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const data = JSON.parse(e.postData.contents || '{}');
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let sheet = ss.getSheetByName(SHEET_NAME);
    if (!sheet) {
      sheet = ss.insertSheet(SHEET_NAME);
      sheet.appendRow(COLUMNS);
      sheet.setFrozenRows(1);
    }
    // מונע הזרקת נוסחאות מתוך שדות הטופס
    const safe = v => {
      const s = String(v == null ? '' : v);
      return /^[=+\-@]/.test(s) ? "'" + s : s;
    };
    sheet.appendRow(COLUMNS.map(c => safe(data[c])));

    if (NOTIFY_EMAIL) {
      MailApp.sendEmail(NOTIFY_EMAIL, 'ליד חדש: ' + (data.name || ''),
        COLUMNS.map(c => c + ': ' + (data[c] || '')).join('\n'));
    }
    return ContentService.createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}
