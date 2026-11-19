/**
 * DataFix Autonomous Engine - Active Database & Storage Service
 * Pure real database: holds 0 records / null by default until user uploads real Excel or CSV files.
 */

const CollegeDataService = {
  getInitialData() {
    const saved = localStorage.getItem("datafix_active_db");
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          return parsed;
        }
      } catch (e) {
        console.warn("Failed to parse saved active DB", e);
      }
    }
    return []; // NULL / EMPTY BY DEFAULT UNTIL USER UPLOADS REAL DATA
  },

  saveData(data) {
    if (data && Array.isArray(data) && data.length > 0) {
      localStorage.setItem("datafix_active_db", JSON.stringify(data));
    } else {
      localStorage.removeItem("datafix_active_db");
    }
  },

  clearData() {
    localStorage.removeItem("datafix_active_db");
    return [];
  },

  getDepartments(dataset) {
    const set = new Set();
    (dataset || []).forEach(item => {
      const dept = item.department || item.Department || item.branch || item.Branch || item.dept;
      if (dept) set.add(String(dept).trim());
    });
    return Array.from(set).sort();
  },

  getSections(dataset, department = null) {
    const set = new Set();
    (dataset || []).forEach(item => {
      const itemDept = item.department || item.Department || item.branch || item.Branch || item.dept;
      if (!department || department === "all" || itemDept === department) {
        const sec = item.section || item.Section || item.sec;
        if (sec) set.add(String(sec).trim());
      }
    });
    return Array.from(set).sort();
  },

  filterByCategory(dataset, { department, section } = {}) {
    return (dataset || []).filter(item => {
      let match = true;
      const itemDept = item.department || item.Department || item.branch || item.Branch || item.dept;
      const itemSec = item.section || item.Section || item.sec;

      if (department && department !== "all") {
        match = match && itemDept === department;
      }
      if (section && section !== "all") {
        match = match && itemSec === section;
      }
      return match;
    });
  }
};

window.CollegeDataService = CollegeDataService;
