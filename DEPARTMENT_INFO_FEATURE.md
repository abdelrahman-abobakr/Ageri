# Department Info Feature - Simplified Department Data

## 🎯 Overview

The new Department Info endpoint provides a simplified view of department information that includes only essential data for public display and navigation. This endpoint excludes sensitive administrative information like budget, location details, and contact information.

## ✅ What's Included

### Department Information
- **Name**: Department name
- **Description**: Short description of the department
- **Labs**: List of labs within the department

### Lab Information (for each lab)
- **Name**: Lab name
- **Description**: Lab description
- **Head**: Lab head researcher name
- **Researchers**: List of researchers in the lab

### Researcher Information (for each researcher)
- **Name**: Researcher full name
- **Position**: Position/role in the lab (e.g., PhD Student, Postdoc, Principal Investigator)

## ❌ What's Excluded

The following fields are **NOT** included in the department info endpoint:

- **Location**: Physical location/address
- **Email**: Department contact email
- **Phone**: Department contact phone
- **Budget**: Financial information
- **Administrative metadata**: Creation dates, update timestamps
- **Status**: Internal status flags
- **Head contact details**: Department head's personal information

## 🔗 API Endpoints

### New Simplified Endpoint
```
GET /api/organization/departments/{id}/info/
```

**Response Format:**
```json
{
    "id": 1,
    "name": "Cell Biology",
    "description": "Department specialized in cell biology research and molecular studies",
    "labs": [
        {
            "id": 1,
            "name": "Molecular Biology Lab",
            "description": "Advanced molecular biology research focusing on gene expression",
            "head_name": "Dr. John Smith",
            "researchers": [
                {
                    "id": 1,
                    "name": "Dr. John Smith",
                    "position": "Principal Investigator"
                },
                {
                    "id": 2,
                    "name": "Dr. Sarah Johnson",
                    "position": "Postdoctoral Researcher"
                }
            ]
        }
    ]
}
```

### Comparison with Other Endpoints

| Endpoint | Purpose | Fields | Access |
|----------|---------|--------|--------|
| `/departments/{id}/info/` | **Public navigation** | Name, description, labs, researchers | Public |
| `/departments/{id}/` | **Full management** | All fields including contact, location | Admin |
| `/departments/` | **Department listing** | Summary fields only | Public |

## 💻 Usage Examples

### Python Example
```python
import requests

# Get simplified department info
response = requests.get('http://localhost:8000/api/organization/departments/1/info/')
if response.status_code == 200:
    dept_info = response.json()
    
    print(f"Department: {dept_info['name']}")
    print(f"Description: {dept_info['description']}")
    
    for lab in dept_info['labs']:
        print(f"\nLab: {lab['name']}")
        print(f"Head: {lab['head_name']}")
        print(f"Description: {lab['description']}")
        
        print("Researchers:")
        for researcher in lab['researchers']:
            print(f"  - {researcher['name']} ({researcher['position']})")
```

### JavaScript/React Example
```javascript
// Fetch department info for navigation component
async function getDepartmentInfo(departmentId) {
    try {
        const response = await fetch(`/api/organization/departments/${departmentId}/info/`);
        const deptInfo = await response.json();
        
        return deptInfo;
    } catch (error) {
        console.error('Error fetching department info:', error);
        return null;
    }
}

// React component example
function DepartmentNavigation({ departmentId }) {
    const [deptInfo, setDeptInfo] = useState(null);
    
    useEffect(() => {
        getDepartmentInfo(departmentId).then(setDeptInfo);
    }, [departmentId]);
    
    if (!deptInfo) return <div>Loading...</div>;
    
    return (
        <div className="department-nav">
            <h2>{deptInfo.name}</h2>
            <p>{deptInfo.description}</p>
            
            <div className="labs">
                {deptInfo.labs.map(lab => (
                    <div key={lab.id} className="lab-item">
                        <h3>{lab.name}</h3>
                        <p>Head: {lab.head_name}</p>
                        <div className="researchers">
                            {lab.researchers.map(researcher => (
                                <span key={researcher.id} className="researcher">
                                    {researcher.name} ({researcher.position})
                                </span>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
```

### cURL Example
```bash
# Test the endpoint
curl -X GET "http://localhost:8000/api/organization/departments/1/info/" \
     -H "Accept: application/json"
```

## 🔧 Implementation Details

### New Serializers Added

1. **`DepartmentInfoSerializer`**
   - Minimal department fields
   - Includes nested labs data
   - Excludes administrative fields

2. **`LabInfoSerializer`**
   - Basic lab information
   - Includes researchers list
   - Excludes location and equipment details

### New View Added

**`DepartmentInfoView`**
- Inherits from `RetrieveAPIView`
- Public access (no authentication required)
- Optimized queries with prefetch_related

### URL Pattern Added
```python
path('departments/<int:pk>/info/', views.DepartmentInfoView.as_view(), name='department-info')
```

## 🎯 Use Cases

### 1. Public Website Navigation
- Display department structure for visitors
- Show research areas and team members
- Provide overview without sensitive data

### 2. Research Collaboration
- Help researchers find collaborators
- Show expertise areas by department
- Display lab capabilities

### 3. Student Information
- Help students understand department structure
- Show potential supervisors and research areas
- Provide contact points for inquiries

### 4. Mobile Applications
- Lightweight data for mobile apps
- Quick department browsing
- Reduced data transfer

## 🔒 Security & Privacy

### Data Protection
- **No sensitive information** exposed
- **No contact details** included
- **No financial data** accessible
- **No administrative metadata** visible

### Access Control
- **Public access** - no authentication required
- **Read-only** - no modification possible
- **Filtered data** - only approved information shown

## 📊 Performance

### Optimizations
- **Prefetch related data** to reduce database queries
- **Minimal fields** to reduce response size
- **Cached queries** for frequently accessed departments
- **Indexed lookups** for fast retrieval

### Response Size
- **Significantly smaller** than full department data
- **Mobile-friendly** payload size
- **Fast loading** for navigation components

## 🧪 Testing

### Test the Endpoint
```bash
# Run the test script
python3 test_department_info.py

# Manual testing
curl http://localhost:8000/api/organization/departments/1/info/
```

### Expected Response
- Status: 200 OK
- Content-Type: application/json
- Body: Department info with labs and researchers

## 🚀 Future Enhancements

### Potential Additions
1. **Research areas** for each lab
2. **Publication counts** per researcher
3. **Equipment highlights** (non-sensitive)
4. **Collaboration opportunities**
5. **Recent achievements**

### Performance Improvements
1. **Response caching** for static data
2. **Pagination** for large departments
3. **Field selection** query parameters
4. **GraphQL support** for flexible queries

## 📝 Summary

The Department Info endpoint provides a **clean, public-friendly view** of department structure that:

✅ **Includes essential information** for navigation and research discovery
✅ **Excludes sensitive data** like location, contact details, and budget
✅ **Optimizes performance** with minimal, focused data
✅ **Supports public access** without authentication requirements
✅ **Enables easy integration** in frontend applications

This feature enhances the user experience by providing exactly the information needed for department browsing and research collaboration, while maintaining privacy and security standards.
