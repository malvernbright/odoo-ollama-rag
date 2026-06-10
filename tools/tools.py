import xmlrpc.client
from langchain_core.tools import tool

# ==========================================
# 1. Odoo Connection Configuration
# ==========================================
ODOO_URL = "http://localhost:8069"
ODOO_DB = "ben_auto"
ODOO_USER = "admin"
ODOO_PASSWORD = "admin"

def get_odoo_models():
    """Helper to establish and authenticate the XML-RPC connection."""
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    if not uid:
        raise Exception("Authentication failed. Check your Odoo credentials and database name.")
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    return uid, models

# ==========================================
# 2. Define ERP Tools (Functions)
# ==========================================
@tool
def get_res_users(limit: int = 5) -> str:
    """
    Fetches a list of active users/employees from the ERP system. 
    Call this when the user asks about system users, employees, or staff.
    """
    try:
        uid, models = get_odoo_models()
        users = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
            'res.users', 'search_read',
            [[('active', '=', True)]],
            {'fields': ['name', 'login'], 'limit': limit}
        )
        if not users:
            return "No active users found in the system."
        return str(users)
    except Exception as e:
        return f"Error fetching users from Odoo: {str(e)}"

@tool
def get_sales_orders(limit: int = 5) -> str:
    """
    Fetches the most recent sales orders from the ERP system.
    Call this when the user asks for sales, orders, quotations, or revenue data.
    """
    try:
        uid, models = get_odoo_models()
        orders = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order', 'search_read',
            [[]], 
            {'fields': ['name', 'partner_id', 'amount_total', 'state'], 'limit': limit}
        )
        if not orders:
            return "No sales orders found."
        return str(orders)
    except Exception as e:
        return f"Error fetching sales orders: {str(e)}. Ensure the Sales module is installed."

@tool
def get_partner_details(search_term: str) -> str:
    """
    Searches for a specific partner, customer, or vendor by name.
    Call this when the user asks for contact details, email, or info about a specific company or person.
    """
    try:
        uid, models = get_odoo_models()
        partners = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'search_read',
            [[('name', 'ilike', search_term)]], 
            {'fields': ['name', 'email', 'phone', 'city'], 'limit': 3}
        )
        if not partners:
            return f"No partner found matching '{search_term}'."
        return str(partners)
    except Exception as e:
        return f"Error fetching partner details: {str(e)}"


@tool
def get_products(search_term: str) -> str:
    """
    Searches for a specific product or products.
    Call this when the user asks for product details, 
    product sales and cost prices, product types, sales and purchase taxes, quantity on hand, Invoicing Policy e.t.c.
    """
    try:
        uid, models = get_odoo_models()
        products = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
            'product.template', 'search_read',
            [[('name', 'ilike', search_term)]], 
            {
                'fields': ['name', 'type', 'list_price', 'taxes_id', 'standard_price', 'categ_id', 'qty_available'], 
                'limit': 300}
        )
        if not products:
            return f"No products found matching '{search_term}'."
        return str(products)
    except Exception as e:
        return f"Error fetching products details: {str(e)}"

@tool
def get_fleet(search_term: str) -> str:
    """
    Searches for vehicles in a fleet.
    Call this when the user asks for vehicle details,
    vehicle model, tags, vehicle driver, future driver, assignment date, vehicle category, order date,
    registration date, cancellation date, chasis number, last odometer reading, fleet manager, location,
    horse power taxation, Deductibility Rates, e.t.c
    """
    try:
        uid, models = get_odoo_models()
        vehicles = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                                     'fleet.vehicle', 'search_read',
                                     [[('display_name', 'ilike', search_term)]],
                                     {
                                         'fields': ['display_name', 'tag_ids', 
                                                    'driver_id', 'future_driver_id', 
                                                    'next_assignation_date', 'category_id'],
                                          'limit': 30
                                     }
                    )
        if not vehicles:
            return f"No vehicles matching {search_term}"
        return str(vehicles)
    except Exception as e:
        return f"Error fetching vehicles details: {str(e)}"