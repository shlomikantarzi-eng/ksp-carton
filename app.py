import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# 1. הגדרות עמוד ועיצוב CSS
# ==========================================
st.set_page_config(
    page_title="מערכת אופטימיזציית אריזה 3D - KSP",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* יישור ימני ועיצוב כללי */
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    /* מרווח עליון מותאם כך שהכותרת תהיה בפריים מלא */
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 0.5rem !important;
        max-width: 98% !important;
    }
    
    /* סרגל צד רחב */
    [data-testid="stSidebar"] {
        min-width: 380px !important;
        max-width: 400px !important;
    }

    /* קופסת פרטי המוצר שנבחר */
    .product-box {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-right: 6px solid #2563eb;
        border-radius: 8px;
        padding: 8px 14px;
        margin-bottom: 8px;
    }
    .product-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0f172a;
    }
    .product-info-line {
        font-size: 0.92rem;
        color: #334155;
        margin-top: 2px;
    }

    /* עיצוב כרטיסיות 4 הקרטונים */
    .carton-card {
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 6px 8px;
        background-color: #ffffff;
        text-align: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .carton-card-selected {
        border: 2px solid #16a34a !important;
        background-color: #f0fdf4 !important;
        box-shadow: 0 3px 8px rgba(22, 163, 74, 0.15);
    }
    .badge-selected {
        background-color: #16a34a;
        color: #ffffff;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 1px 6px;
        border-radius: 4px;
        display: inline-block;
    }
    .badge-normal {
        background-color: #64748b;
        color: #ffffff;
        font-size: 0.75rem;
        padding: 1px 6px;
        border-radius: 4px;
        display: inline-block;
    }
    .carton-title {
        font-size: 0.92rem;
        font-weight: 700;
        color: #1e293b;
        margin: 4px 0 2px 0;
    }
    .carton-img-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 48px;
        margin: 2px 0;
    }
    .dims-breakdown {
        font-size: 0.82rem;
        color: #334155;
        background-color: #f8fafc;
        border-radius: 5px;
        padding: 4px;
        margin-top: 4px;
        border: 1px solid #e2e8f0;
        line-height: 1.3;
    }
    .carton-util {
        font-size: 0.85rem;
        font-weight: 700;
        color: #15803d;
        margin-top: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# כותרת ראשית קומפקטית ובפריים
st.markdown(
    "<h3 style='margin: 0 0 6px 0; color: #0f172a;'>📦 מערכת אופטימיזציית"
    " אריזה ותצוגת תלת-ממד (3D)</h3>",
    unsafe_allow_html=True,
)

# ==========================================
# 2. הגדרת 4 הקרטונים + איורי SVG מותאמים ויזואלית
# ==========================================
CARTONS = {
    "קבוצה 1": {
        "title": "קבוצה 1 (סטנדרטית)",
        "L": 880.0,
        "W": 481.0,
        "H": 295.0,
        "color": "#1f77b4",
        # איור קופסה פרופורציונלית בינונית
        "svg": """<svg width="60" height="42" viewBox="0 0 70 45"><path d="M35 5 L60 16 L35 27 L10 16 Z" fill="#f59e0b" stroke="#b45309"/><path d="M10 16 L35 27 L35 42 L10 31 Z" fill="#d97706" stroke="#b45309"/><path d="M35 27 L60 16 L60 31 L35 42 Z" fill="#b45309" stroke="#78350f"/></svg>""",
    },
    "קבוצה 2": {
        "title": "קבוצה 2 (רחבה/ארוכה)",
        "L": 1910.0,
        "W": 880.0,
        "H": 390.0,
        "color": "#ff7f0e",
        # איור קופסה רחבה ושטוחה
        "svg": """<svg width="75" height="35" viewBox="0 0 85 40"><path d="M42.5 5 L80 14 L42.5 23 L5 14 Z" fill="#f59e0b" stroke="#b45309"/><path d="M5 14 L42.5 23 L42.5 35 L5 26 Z" fill="#d97706" stroke="#b45309"/><path d="M42.5 23 L80 14 L80 26 L42.5 35 Z" fill="#b45309" stroke="#78350f"/></svg>""",
    },
    "קבוצה 3": {
        "title": "קבוצה 3 (נפחית/גבוהה)",
        "L": 1020.0,
        "W": 830.0,
        "H": 670.0,
        "color": "#9467bd",
        # איור קופסה קוביותית וגבוהה
        "svg": """<svg width="50" height="48" viewBox="0 0 60 55"><path d="M30 4 L52 14 L30 24 L8 14 Z" fill="#f59e0b" stroke="#b45309"/><path d="M8 14 L30 24 L30 50 L8 40 Z" fill="#d97706" stroke="#b45309"/><path d="M30 24 L52 14 L52 40 L30 50 Z" fill="#b45309" stroke="#78350f"/></svg>""",
    },
    "קבוצה 4": {
        "title": "קבוצה 4 (ארוכה/צרה)",
        "L": 2030.0,
        "W": 460.0,
        "H": 290.0,
        "color": "#17becf",
        # איור קופסה צרה, ארוכה ונמוכה (כמו שרוול)
        "svg": """<svg width="80" height="30" viewBox="0 0 90 32"><path d="M45 4 L85 10 L45 16 L5 10 Z" fill="#f59e0b" stroke="#b45309"/><path d="M5 10 L45 16 L45 28 L5 22 Z" fill="#d97706" stroke="#b45309"/><path d="M45 16 L85 10 L85 22 L45 28 Z" fill="#b45309" stroke="#78350f"/></svg>""",
    },
}


# ==========================================
# 3. טעינת הנתונים
# ==========================================
@st.cache_data(ttl=600)
def load_all_products():
  try:
    df = pd.read_csv("products.csv")
    cols = {str(c).strip(): str(c).strip() for c in df.columns}
    df.rename(columns=cols, inplace=True)

    sku_col = next(
        (
            c
            for c in df.columns
            if "sku" in c.lower() or "מק" in c or "id" in c.lower()
        ),
        df.columns[0],
    )
    name_col = next(
        (
            c
            for c in df.columns
            if "name" in c.lower()
            or "item" in c.lower()
            or "שם" in c
            or "desc" in c.lower()
        ),
        df.columns[1],
    )
    l_col = next(
        (
            c
            for c in df.columns
            if "box_l" in c.lower()
            or "length" in c.lower()
            or c.lower() == "l"
            or "אורך" in c
        ),
        None,
    )
    w_col = next(
        (
            c
            for c in df.columns
            if "box_w" in c.lower()
            or "width" in c.lower()
            or c.lower() == "w"
            or "רוחב" in c
        ),
        None,
    )
    h_col = next(
        (
            c
            for c in df.columns
            if "box_h" in c.lower()
            or "height" in c.lower()
            or c.lower() == "h"
            or "גובה" in c
        ),
        None,
    )

    if l_col and w_col and h_col:
      df_clean = df[[sku_col, name_col, l_col, w_col, h_col]].copy()
      df_clean.columns = ["SKU", "Item_Name", "Box_L", "Box_W", "Box_H"]

      df_clean["SKU"] = (
          df_clean["SKU"]
          .astype(str)
          .apply(lambda x: x.replace(".0", "") if x.endswith(".0") else x)
      )
      df_clean["Box_L"] = pd.to_numeric(df_clean["Box_L"], errors="coerce")
      df_clean["Box_W"] = pd.to_numeric(df_clean["Box_W"], errors="coerce")
      df_clean["Box_H"] = pd.to_numeric(df_clean["Box_H"], errors="coerce")
      df_clean.dropna(subset=["Box_L", "Box_W", "Box_H"], inplace=True)
      return df_clean, "CSV"
  except Exception:
    pass

  mock_df = pd.DataFrame([
      {
          "SKU": "100019",
          "Item_Name": "Hemilton 20 Inch Standing Fan 3 Speeds HEM-632",
          "Box_L": 690.0,
          "Box_W": 560.0,
          "Box_H": 140.0,
      },
      {
          "SKU": "200045",
          "Item_Name": "מקלדת מכנית גיימינג אלחוטית",
          "Box_L": 450.0,
          "Box_W": 150.0,
          "Box_H": 40.0,
      },
  ])
  return mock_df, "Mock"


df_items, data_source = load_all_products()

if data_source == "CSV":
  st.sidebar.success(f'🟢 נטענו {len(df_items)} מק"טים מקובץ ה-CSV!')
else:
  st.sidebar.info('💡 העלה קובץ products.csv לטעינת כל המאגר.')

# ==========================================
# 4. סיידבאר: לבחירת מוצר
# ==========================================
st.sidebar.header("🔎 איתור מוצר מהמלאי")
search_mode = st.sidebar.radio(
    "שיטת בחירה:", ["בחירה מרשימת המק\"טים המלאה", "הזנת מידות ידנית"]
)

item_L, item_W, item_H = 0.0, 0.0, 0.0
item_name_full = ""
sku_val = ""

if search_mode == 'בחירה מרשימת המק"טים המלאה':
  df_items["display_name"] = (
      df_items["SKU"] + " - " + df_items["Item_Name"].fillna("ללא שם")
  )
  selected_display = st.sidebar.selectbox(
      f'חפש או בחר מק"ט ({len(df_items)} זמינים):',
      options=df_items["display_name"].tolist(),
  )

  selected_row = df_items[df_items["display_name"] == selected_display].iloc[0]
  item_L = float(selected_row["Box_L"])
  item_W = float(selected_row["Box_W"])
  item_H = float(selected_row["Box_H"])
  item_name_full = str(selected_row["Item_Name"])
  sku_val = str(selected_row["SKU"])
else:
  st.sidebar.subheader("מידות המוצר (מ\"מ)")
  item_L = st.sidebar.number_input("אורך L", min_value=10.0, value=500.0)
  item_W = st.sidebar.number_input("רוחב W", min_value=10.0, value=300.0)
  item_H = st.sidebar.number_input("גובה H", min_value=10.0, value=150.0)
  item_name_full = "מוצר בהזנה ידנית"
  sku_val = "ידני"

# ==========================================
# 5. לוגיקת התאמת קרטון
# ==========================================
item_volume = item_L * item_W * item_H
valid_options = []

for key, dims in CARTONS.items():
  if item_L <= dims["L"] and item_W <= dims["W"] and item_H <= dims["H"]:
    carton_vol = dims["L"] * dims["W"] * dims["H"]
    utilization = (item_volume / carton_vol) * 100
    waste = carton_vol - item_volume
    valid_options.append({
        "key": key,
        "dims": dims,
        "utilization": utilization,
        "waste": waste,
    })

best_carton_key = (
    min(valid_options, key=lambda x: x["waste"])["key"]
    if valid_options
    else None
)

# ==========================================
# 6. תצוגת פרטי המוצר
# ==========================================
st.markdown(
    f"""<div class="product-box">
        <div class="product-title">🛒 מוצר שנבחר: {item_name_full}</div>
        <div class="product-info-line"><b>מק"ט:</b> {sku_val}</div>
        <div class="product-info-line"><b>מידות המוצר:</b> אורך <b>{int(item_L)}</b> מ"מ | רוחב <b>{int(item_W)}</b> מ"מ | גובה <b>{int(item_H)}</b> מ"מ</div>
    </div>""",
    unsafe_allow_html=True,
)

# ==========================================
# 7. מפרט 4 הקרטונים במחסן (נקי ללא תגיות זולגות)
# ==========================================
st.markdown(
    "<div style='font-weight: 700; font-size: 0.98rem; margin: 2px 0 4px 0;'>📋"
    " מפרט הקרטונים במחסן והתאמה:</div>",
    unsafe_allow_html=True,
)

cols = st.columns(4)

for idx, (key, dims) in enumerate(CARTONS.items()):
  is_selected = key == best_carton_key

  card_class = "carton-card carton-card-selected" if is_selected else "carton-card"
  badge = (
      '<span class="badge-selected">🎯 נבחר עבור המוצר</span>'
      if is_selected
      else '<span class="badge-normal">זמין במחסן</span>'
  )

  util_html = ""
  if is_selected and valid_options:
    best_opt = next(o for o in valid_options if o["key"] == key)
    util_html = (
        f'<div class="carton-util">ניצול נפח:'
        f' {best_opt["utilization"]:.1f}%</div>'
    )

  card_html = (
      f'<div class="{card_class}">{badge}<div'
      f' class="carton-img-container">{dims["svg"]}</div><div'
      f' class="carton-title">{dims["title"]}</div><div'
      f' class="dims-breakdown"><b>אורך:</b> {int(dims["L"])} מ"מ<br><b>רוחב:</b>'
      f' {int(dims["W"])} מ"מ<br><b>גובה:</b> {int(dims["H"])}'
      f" מ\"מ</div>{util_html}</div>"
  )

  cols[idx].markdown(card_html, unsafe_allow_html=True)

# ==========================================
# 8. הדמיית תלת-ממד (3D) גבוהה ונגישה במרכז המסך
# ==========================================
if not valid_options:
  st.error(
      f"🚨 המוצר **{item_name_full}** ({item_L}x{item_W}x{item_H} מ\"מ) חורג"
      " ממידות כל 4 הקרטונים במחסן!"
  )
else:
  best = min(valid_options, key=lambda x: x["waste"])


  def get_box_lines(x0, y0, z0, dx, dy, dz, name, color):
    x = [
        x0,
        x0 + dx,
        x0 + dx,
        x0,
        x0,
        x0,
        x0 + dx,
        x0 + dx,
        x0,
        x0,
        x0 + dx,
        x0 + dx,
        x0 + dx,
        x0 + dx,
        x0,
        x0,
    ]
    y = [
        y0,
        y0,
        y0 + dy,
        y0 + dy,
        y0,
        y0,
        y0,
        y0 + dy,
        y0 + dy,
        y0 + dy,
        y0 + dy,
        y0,
        y0,
        y0 + dy,
        y0 + dy,
        y0,
    ]
    z = [
        z0,
        z0,
        z0,
        z0,
        z0,
        z0 + dz,
        z0 + dz,
        z0 + dz,
        z0 + dz,
        z0,
        z0,
        z0,
        z0 + dz,
        z0 + dz,
        z0 + dz,
        z0 + dz,
    ]
    return go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="lines",
        name=name,
        line=dict(color=color, width=3),
    )


  def get_box_mesh(x0, y0, z0, dx, dy, dz, name, color, opacity=0.3):
    x = [x0, x0 + dx, x0 + dx, x0, x0, x0 + dx, x0 + dx, x0]
    y = [y0, y0, y0 + dy, y0 + dy, y0, y0, y0 + dy, y0 + dy]
    z = [z0, z0, z0, z0, z0 + dz, z0 + dz, z0 + dz, z0 + dz]
    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]
    return go.Mesh3d(
        x=x,
        y=y,
        z=z,
        i=i,
        j=j,
        k=k,
        name=name,
        color=color,
        opacity=opacity,
        showscale=False,
    )


  fig = go.Figure()

  # קרטון חיצוני
  fig.add_trace(
      get_box_mesh(
          0,
          0,
          0,
          best["dims"]["L"],
          best["dims"]["W"],
          best["dims"]["H"],
          best["dims"]["title"],
          best["dims"]["color"],
          opacity=0.15,
      )
  )
  fig.add_trace(
      get_box_lines(
          0,
          0,
          0,
          best["dims"]["L"],
          best["dims"]["W"],
          best["dims"]["H"],
          "מסגרת קרטון",
          best["dims"]["color"],
      )
  )

  # מוצר פנימי
  fig.add_trace(
      get_box_mesh(
          0, 0, 0, item_L, item_W, item_H, "המוצר", "green", opacity=0.75
      )
  )
  fig.add_trace(
      get_box_lines(0, 0, 0, item_L, item_W, item_H, "מסגרת מוצר", "darkgreen")
  )

  fig.update_layout(
      title=dict(
          text=f"<b>הדמיית אריזה בתלת-ממד עבור {best['dims']['title']}</b>",
          x=0.5,
      ),
      scene=dict(
          xaxis_title='אורך (מ"מ)',
          yaxis_title='רוחב (מ"מ)',
          zaxis_title='גובה (מ"מ)',
          aspectmode="data",
      ),
      height=440,  # גובה קומפקטי שנכנס בדיוק במסך המסך
      margin=dict(l=5, r=5, b=5, t=25),
  )

  st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 9. טבלה מתקפלת לצפייה בכל המאגר
# ==========================================
with st.expander(
    f'📋 לחץ כאן לצפייה וחיפוש בכל רשימת המק"טים ({len(df_items)} פריטים)'
):
  st.dataframe(
      df_items[["SKU", "Item_Name", "Box_L", "Box_W", "Box_H"]],
      use_container_width=True,
  )
