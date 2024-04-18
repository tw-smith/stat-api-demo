import {
  Box,
  FormControl,
  FormHelperText,
  Input,
  InputLabel,
  MenuItem,
  Select,
  Slider,
  Stack
} from '@mui/material'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import { useDispatch, useSelector } from 'react-redux'
import 'react-tooltip/dist/react-tooltip.css'
import { setshowSearchByGeom } from '../../redux/slices/mainSlice'
import { newSearch } from '../../utils/searchHelper'
import './Filter.css'

// const SELECTED_PRODUCT = {
//   type: 'Product',
//   conformsTo: [
//     'https://api.statspec.org/geojson#polygon',
//     'https://api.statspec.org/geojson#multipolygon'
//   ],
//   id: 'umbra_archive_catalog',
//   title: 'Umbra Archive Catalog',
//   description:
//     'Umbra SAR Images served by the Archive Catalog. Way more detail here or a link down in links to Product documentation.',
//   keywords: ['SAR', 'Archive'],
//   license: 'CC-BY-4.0',
//   providers: {
//     name: 'Umbra',
//     description: 'Global Omniscience',
//     roles: ['producer'],
//     url: 'https://umbra.space'
//   },
//   links: {
//     href: 'https://docs.canopy.umbra.space/',
//     rel: 'documentation',
//     type: 'docs',
//     title: 'Canopy Documentation'
//   },
//   parameters: {
//     description: 'Umbra Archive Catalog Parameters docstring yay!',
//     properties: {
//       'sar:resolution_range': {
//         type: 'number',
//         minimum: 0.25,
//         maximum: 1,
//         description:
//           'The range resolution of the SAR Image. This is equivalent to the resolution of the ground plane projected GEC Cloud-Optimized Geotiff',
//         title: 'Range Resolution (m)'
//       },
//       'sar:looks_azimuth': {
//         type: 'number',
//         minimum: 1,
//         maximum: 10,
//         description:
//           'The azimuth looks in the SAR Image. This value times the sar:resolution_range gives the azimuth resolution of the complex products.',
//         title: 'Looks Azimuth (m)'
//       },
//       platform: {
//         description: 'The satellites to consider for this Opportunity.',
//         title: 'Platform (Satellite)',
//         type: 'string',
//         regex: 'Umbra-\\d{2}'
//       }
//     },
//     title: 'UmbraArchiveCatalogParameters',
//     type: 'object'
//   }
// }

const Filter = () => {
  const dispatch = useDispatch()
  const _selectedCollectionData = useSelector(
    (state) => state.mainSlice.selectedCollectionData
  )
  const _selectedProductData = useSelector(
    (state) => state.mainSlice.selectedProductData
  )

  const _viewMode = useSelector((state) => state.mainSlice.viewMode)
  const _searchGeojsonBoundary = useSelector(
    (state) => state.mainSlice.searchGeojsonBoundary
  )
  const _appConfig = useSelector((state) => state.mainSlice.appConfig)
  const mosaicTilerURL = _appConfig.MOSAIC_TILER_URL || ''

  const theme = createTheme({
    components: {
      MuiFormControlLabel: {
        styleOverrides: {
          label: {
            color: '#fff'
          },
          root: {
            color: '#fff'
          }
        }
      },
      MuiFormHelperText: {
        styleOverrides: {
          root: {
            color: '#fff'
          }
        }
      },

      MuiSelect: {
        styleOverrides: {
          root: {
            color: '#fff'
          }
        }
      },

      MuiSwitch: {
        styleOverrides: {
          switchBase: {
            color: '#fff'
          },
          colorPrimary: {
            '&.Mui-checked': {
              color: '#fff'
            }
          },
          track: {
            backgroundColor: '#dedede',
            '.Mui-checked.Mui-checked + &': {
              backgroundColor: '#6cc24a'
            }
          }
        }
      }
    }
  })

  const filterContainer = []
  if (_selectedProductData?.parameters?.properties) {
    for (const constraintName of Object.keys(
      _selectedProductData.parameters.properties
    )) {
      const constraint =
        _selectedProductData.parameters.properties[constraintName]
      if (constraint.type === 'number') {
        filterContainer.push(
          <FormControl key={constraintName} sx={{ marginTop: 4 }}>
            <InputLabel
              htmlFor={constraintName}
              sx={{ color: '#FFF', paddingTop: 2 }}
            >
              {constraint.title}
            </InputLabel>
            <Slider
              id={constraintName}
              name={constraintName}
              defaultValue={30}
              valueLabelDisplay="on"
            />
            <FormHelperText sx={{ color: '#FFF', paddingTop: 3.5 }}>
              {constraint.description}
            </FormHelperText>
          </FormControl>
        )
        continue
      }

      if (constraint.type === 'string') {
        filterContainer.push(
          <FormControl key={constraintName}>
            <InputLabel
              htmlFor={constraintName}
              sx={{ color: '#FFF', paddingTop: 0 }}
            >
              {constraint.title}
            </InputLabel>
            <Input
              id={constraintName}
              name={constraintName}
              aria-describedby={constraintName}
            />
            <FormHelperText>{constraint.description}</FormHelperText>
          </FormControl>
        )
        continue
      }

      if (constraint.type === 'array') {
        let refItem = {}
        if (constraint.items.$ref) {
          const refName = constraint.items.$ref.split('/').pop()
          refItem = _selectedProductData.parameters.$defs[refName]
        }

        const options = []

        for (const option of refItem?.enum || []) {
          options.push(
            <MenuItem key={option} value={option}>
              {option}
            </MenuItem>
          )
        }

        filterContainer.push(
          <FormControl key={constraintName}>
            <InputLabel
              htmlFor={constraintName}
              sx={{ color: '#FFF', paddingTop: 0 }}
            >
              {constraint.title}
            </InputLabel>
            <Select id={constraintName} name={constraintName}>
              {options}
            </Select>
            <FormHelperText>{constraint.description}</FormHelperText>
          </FormControl>
        )
        continue
      }
    }
  }

  function processSearchBtn(formEvent) {
    formEvent.preventDefault()

    const keys = Object.keys(formEvent.target).slice(0, -2)
    let res = {}

    for (const key of keys) {
      if (formEvent.target[key].value) {
        res = {
          ...res,
          [formEvent.target[key].name]: formEvent.target[key].value
        }
      }
    }

    console.log('Parameters: ', res)
    newSearch(res)
    // dispatch(setshowSearchByGeom(false))
  }

  return (
    <ThemeProvider theme={theme}>
      <div className="" data-testid="Search">
        <form onSubmit={processSearchBtn}>
          <Stack gap={4}>{filterContainer}</Stack>

          <div className="" style={{ marginTop: 24 }}>
            <button className={`actionButton searchButton`} type="submit">
              Search
            </button>
          </div>
        </form>
      </div>
    </ThemeProvider>
  )
}

export default Filter
