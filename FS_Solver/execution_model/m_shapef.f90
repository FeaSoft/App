! Description:
! Element shape functions and integration points.
module m_shapef
    use linear_algebra
    use data_model
    implicit none
    
    private
    public eval_functs, eval_derivs
    
    ! error messages
    character(*), parameter :: ERROR_UNDEFINED_INTEGRATION_POINT = 'ERROR: Undefined integration point.'
    
    contains
    
    ! Description:
    ! Get natural coordinates and weights of integration points.
    subroutine get_ip(element, i_ip, r, s, t, weight)
        ! procedure arguments
        type(t_element), intent(in)  :: element ! finite element
        integer,         intent(in)  :: i_ip    ! integration point index
        real,            intent(out) :: r, s, t ! natural coordinates
        real,            intent(out) :: weight  ! integration weight
        
        ! get natural coordinates and weights based on element type
        select case (element%t_element)
            case (E2D3)
                select case (i_ip)
                    case (1); r = 0.3333333333333333; s = 0.3333333333333333; t = 0.0; weight = 0.5
                    case default; error stop ERROR_UNDEFINED_INTEGRATION_POINT
                end select
            case (E2D4)
                select case (i_ip)
                    case (1); r = -0.5773502691896258; s = -0.5773502691896258; t = 0.0; weight = 1.0
                    case (2); r = +0.5773502691896258; s = -0.5773502691896258; t = 0.0; weight = 1.0
                    case (3); r = +0.5773502691896258; s = +0.5773502691896258; t = 0.0; weight = 1.0
                    case (4); r = -0.5773502691896258; s = +0.5773502691896258; t = 0.0; weight = 1.0
                    case default; error stop ERROR_UNDEFINED_INTEGRATION_POINT
                end select
            case (E3D4)
                select case (i_ip)
                    case (1); r = 0.25; s = 0.25; t = 0.25; weight = 0.1666666666666667
                    case default; error stop ERROR_UNDEFINED_INTEGRATION_POINT
                end select
            case (E3D5)
                select case (i_ip)
                    case (1); r = +0.5; s = +0.0; t = +0.1531754163448146; weight = 0.1333333333333333
                    case (2); r = +0.0; s = +0.5; t = +0.1531754163448146; weight = 0.1333333333333333
                    case (3); r = -0.5; s = +0.0; t = +0.1531754163448146; weight = 0.1333333333333333
                    case (4); r = +0.0; s = -0.5; t = +0.1531754163448146; weight = 0.1333333333333333
                    case (5); r = +0.0; s = +0.0; t = +0.6372983346207416; weight = 0.1333333333333333
                    case default; error stop ERROR_UNDEFINED_INTEGRATION_POINT
                end select
            case (E3D6)
                select case (i_ip)
                    case (1); r = -0.5773502691896258; s = 0.5; t = 0.5; weight = 0.1666666666666667
                    case (2); r = -0.5773502691896258; s = 0.0; t = 0.5; weight = 0.1666666666666667
                    case (3); r = -0.5773502691896258; s = 0.5; t = 0.0; weight = 0.1666666666666667
                    case (4); r = +0.5773502691896258; s = 0.5; t = 0.5; weight = 0.1666666666666667
                    case (5); r = +0.5773502691896258; s = 0.0; t = 0.5; weight = 0.1666666666666667
                    case (6); r = +0.5773502691896258; s = 0.5; t = 0.0; weight = 0.1666666666666667
                    case default; error stop ERROR_UNDEFINED_INTEGRATION_POINT
                end select
            case (E3D8)
                select case (i_ip)
                    case (1); r = -0.5773502691896258; s = -0.5773502691896258; t = -0.5773502691896258; weight = 1.0
                    case (2); r = +0.5773502691896258; s = -0.5773502691896258; t = -0.5773502691896258; weight = 1.0
                    case (3); r = +0.5773502691896258; s = +0.5773502691896258; t = -0.5773502691896258; weight = 1.0
                    case (4); r = -0.5773502691896258; s = +0.5773502691896258; t = -0.5773502691896258; weight = 1.0
                    case (5); r = -0.5773502691896258; s = -0.5773502691896258; t = +0.5773502691896258; weight = 1.0
                    case (6); r = +0.5773502691896258; s = -0.5773502691896258; t = +0.5773502691896258; weight = 1.0
                    case (7); r = +0.5773502691896258; s = +0.5773502691896258; t = +0.5773502691896258; weight = 1.0
                    case (8); r = -0.5773502691896258; s = +0.5773502691896258; t = +0.5773502691896258; weight = 1.0
                    case default; error stop ERROR_UNDEFINED_INTEGRATION_POINT
                end select
            case default
                error stop ERROR_UNDEFINED_ELEMENT_TYPE
        end select
    end subroutine
    
    ! Description:
    ! Evaluate element shape functions at natural coordinates.
    type(t_matrix) function eval_functs(element, i_ip) result(N)
        ! procedure arguments
        type(t_element), intent(in) :: element ! finite element
        integer,         intent(in) :: i_ip    ! integration point index
        
        ! additional variables
        real :: r, s, t, weight ! integration point coordinates and weight
        real :: N1, N2, N3, N4  ! value of shape functions
        real :: N5, N6, N7, N8  ! ...
        
        ! get integration point coordinates and weight
        call get_ip(element, i_ip, r, s, t, weight)
        
        ! evaluate shape functions based on element type
        select case (element%t_element)
            case (E2D3)
                N1 = 1.0 - r - s
                N2 = r
                N3 = s
                N = new_matrix(2, 6)
                N%at(1, :) = [ N1, 0.0,  N2, 0.0,  N3, 0.0]
                N%at(2, :) = [0.0,  N1, 0.0,  N2, 0.0,  N3]
            case (E2D4)
                N1 = 0.25*(1.0 - r)*(1.0 - s)
                N2 = 0.25*(1.0 + r)*(1.0 - s)
                N3 = 0.25*(1.0 + r)*(1.0 + s)
                N4 = 0.25*(1.0 - r)*(1.0 + s)
                N = new_matrix(2, 8)
                N%at(1, :) = [ N1, 0.0,  N2, 0.0,  N3, 0.0,  N4, 0.0]
                N%at(2, :) = [0.0,  N1, 0.0,  N2, 0.0,  N3, 0.0,  N4]
            case (E3D4)
                N1 = 1.0 - r - s - t
                N2 = r
                N3 = s
                N4 = t
                N = new_matrix(3, 12)
                N%at(1, :) = [ N1, 0.0, 0.0,  N2, 0.0, 0.0,  N3, 0.0, 0.0,  N4, 0.0, 0.0]
                N%at(2, :) = [0.0,  N1, 0.0, 0.0,  N2, 0.0, 0.0,  N3, 0.0, 0.0,  N4, 0.0]
                N%at(3, :) = [0.0, 0.0,  N1, 0.0, 0.0,  N2, 0.0, 0.0,  N3, 0.0, 0.0,  N4]
            case (E3D5)
                N1 = 0.25*(-r + s + t - 1.0)*(-r - s + t - 1.0)/(1.0 - t)
                N2 = 0.25*(-r - s + t - 1.0)*(+r - s + t - 1.0)/(1.0 - t)
                N3 = 0.25*(+r + s + t - 1.0)*(+r - s + t - 1.0)/(1.0 - t)
                N4 = 0.25*(+r + s + t - 1.0)*(-r + s + t - 1.0)/(1.0 - t)
                N5 = t
                N = new_matrix(3, 15)
                N%at(1, :) = [ N1, 0.0, 0.0,  N2, 0.0, 0.0,  N3, 0.0, 0.0,  N4, 0.0, 0.0,  N5, 0.0, 0.0]
                N%at(2, :) = [0.0,  N1, 0.0, 0.0,  N2, 0.0, 0.0,  N3, 0.0, 0.0,  N4, 0.0, 0.0,  N5, 0.0]
                N%at(3, :) = [0.0, 0.0,  N1, 0.0, 0.0,  N2, 0.0, 0.0,  N3, 0.0, 0.0,  N4, 0.0, 0.0,  N5]
            case (E3D6)
                N1 = 0.5*(1.0 - r)*s
                N2 = 0.5*(1.0 - r)*t
                N3 = 0.5*(1.0 - r)*(1.0 - s - t)
                N4 = 0.5*(1.0 + r)*s
                N5 = 0.5*(1.0 + r)*t
                N6 = 0.5*(1.0 + r)*(1.0 - s - t)
                N = new_matrix(3, 18)
                N%at(1, :) = [ N1, 0.0, 0.0,  N2, 0.0, 0.0,  N3, 0.0, 0.0,  N4, 0.0, 0.0,  N5, 0.0, 0.0,  N6, 0.0, 0.0]
                N%at(2, :) = [0.0,  N1, 0.0, 0.0,  N2, 0.0, 0.0,  N3, 0.0, 0.0,  N4, 0.0, 0.0,  N5, 0.0, 0.0,  N6, 0.0]
                N%at(3, :) = [0.0, 0.0,  N1, 0.0, 0.0,  N2, 0.0, 0.0,  N3, 0.0, 0.0,  N4, 0.0, 0.0,  N5, 0.0, 0.0,  N6]
            case (E3D8)
                N1 = 0.125*(1.0 - r)*(1.0 - s)*(1.0 - t)
                N2 = 0.125*(1.0 + r)*(1.0 - s)*(1.0 - t)
                N3 = 0.125*(1.0 + r)*(1.0 + s)*(1.0 - t)
                N4 = 0.125*(1.0 - r)*(1.0 + s)*(1.0 - t)
                N5 = 0.125*(1.0 - r)*(1.0 - s)*(1.0 + t)
                N6 = 0.125*(1.0 + r)*(1.0 - s)*(1.0 + t)
                N7 = 0.125*(1.0 + r)*(1.0 + s)*(1.0 + t)
                N8 = 0.125*(1.0 - r)*(1.0 + s)*(1.0 + t)
                N = new_matrix(3, 24)
                N%at(1, :) = [ N1, 0.0, 0.0,  N2, 0.0, 0.0,  N3, 0.0, 0.0,  N4, 0.0, 0.0,  N5, 0.0, 0.0,  N6, 0.0, 0.0,  N7, 0.0, 0.0,  N8, 0.0, 0.0]
                N%at(2, :) = [0.0,  N1, 0.0, 0.0,  N2, 0.0, 0.0,  N3, 0.0, 0.0,  N4, 0.0, 0.0,  N5, 0.0, 0.0,  N6, 0.0, 0.0,  N7, 0.0, 0.0,  N8, 0.0]
                N%at(3, :) = [0.0, 0.0,  N1, 0.0, 0.0,  N2, 0.0, 0.0,  N3, 0.0, 0.0,  N4, 0.0, 0.0,  N5, 0.0, 0.0,  N6, 0.0, 0.0,  N7, 0.0, 0.0,  N8]
            case default
                error stop ERROR_UNDEFINED_ELEMENT_TYPE
        end select
    end function
    
    ! Description:
    ! Evaluate natural derivatives of element shape functions at natural coordinates.
    type(t_matrix) function eval_derivs(element, i_ip, ip_weight) result(Nr)
        ! procedure arguments
        type(t_element), intent(in)  :: element   ! finite element
        integer,         intent(in)  :: i_ip      ! integration point index
        real, optional,  intent(out) :: ip_weight ! integration point weight
        
        ! additional variables
        real :: r, s, t, weight                        ! integration point coordinates and weight
        real :: N1r, N2r, N3r, N4r, N5r, N6r, N7r, N8r ! natural derivatives of shape functions (dNi/dr)
        real :: N1s, N2s, N3s, N4s, N5s, N6s, N7s, N8s ! natural derivatives of shape functions (dNi/ds)
        real :: N1t, N2t, N3t, N4t, N5t, N6t, N7t, N8t ! natural derivatives of shape functions (dNi/dt)
        
        ! get integration point coordinates and weight
        call get_ip(element, i_ip, r, s, t, weight)
        if (present(ip_weight)) ip_weight = weight
        
        ! evaluate natural derivatives of shape functions based on element type
        select case (element%t_element)
            case (E2D3)
                N1r = -1.0; N1s = -1.0
                N2r = +1.0; N2s = +0.0
                N3r = +0.0; N3s = +1.0
                Nr = new_matrix(2, 3)
                Nr%at(1, :) = [N1r, N2r, N3r]
                Nr%at(2, :) = [N1s, N2s, N3s]
            case (E2D4)
                N1r = 0.25*(-1.0 + s); N1s = 0.25*(-1.0 + r)
                N2r = 0.25*(+1.0 - s); N2s = 0.25*(-1.0 - r)
                N3r = 0.25*(+1.0 + s); N3s = 0.25*(+1.0 + r)
                N4r = 0.25*(-1.0 - s); N4s = 0.25*(+1.0 - r)
                Nr = new_matrix(2, 4)
                Nr%at(1, :) = [N1r, N2r, N3r, N4r]
                Nr%at(2, :) = [N1s, N2s, N3s, N4s]
            case (E3D4)
                N1r = -1.0; N1s = -1.0; N1t = -1.0
                N2r = +1.0; N2s = +0.0; N2t = +0.0
                N3r = +0.0; N3s = +1.0; N3t = +0.0
                N4r = +0.0; N4s = +0.0; N4t = +1.0
                Nr = new_matrix(3, 4)
                Nr%at(1, :) = [N1r, N2r, N3r, N4r]
                Nr%at(2, :) = [N1s, N2s, N3s, N4s]
                Nr%at(3, :) = [N1t, N2t, N3t, N4t]
            case (E3D5)
                N1r = 0.5/(t - 1.0)*(-r + t - 1.0); N1s = 0.5/(t - 1.0)*s             ; N1t = 0.25*(+(r*r) - (s*s) - (t*t) + (2.0*t) - 1.0)/(t - 1.0)**2.0
                N2r = 0.5/(t - 1.0)*r             ; N2s = 0.5/(t - 1.0)*(-s + t - 1.0); N2t = 0.25*(-(r*r) + (s*s) - (t*t) + (2.0*t) - 1.0)/(t - 1.0)**2.0
                N3r = 0.5/(t - 1.0)*(-r - t + 1.0); N3s = 0.5/(t - 1.0)*s             ; N3t = 0.25*(+(r*r) - (s*s) - (t*t) + (2.0*t) - 1.0)/(t - 1.0)**2.0
                N4r = 0.5/(t - 1.0)*r             ; N4s = 0.5/(t - 1.0)*(-s - t + 1.0); N4t = 0.25*(-(r*r) + (s*s) - (t*t) + (2.0*t) - 1.0)/(t - 1.0)**2.0
                N5r = 0.0                         ; N5s = 0.0                         ; N5t = 1.0
                Nr = new_matrix(3, 5)
                Nr%at(1, :) = [N1r, N2r, N3r, N4r, N5r]
                Nr%at(2, :) = [N1s, N2s, N3s, N4s, N5s]
                Nr%at(3, :) = [N1t, N2t, N3t, N4t, N5t]
            case (E3D6)
                N1r = -0.5*s            ; N1s = 0.5*(+1.0 - r); N1t = 0.0
                N2r = -0.5*t            ; N2s = 0.0           ; N2t = 0.5*(+1.0 - r)
                N3r = -0.5*(1.0 - s - t); N3s = 0.5*(-1.0 + r); N3t = 0.5*(-1.0 + r)
                N4r = +0.5*s            ; N4s = 0.5*(+1.0 + r); N4t = 0.0
                N5r = +0.5*t            ; N5s = 0.0           ; N5t = 0.5*(+1.0 + r)
                N6r = +0.5*(1.0 - s - t); N6s = 0.5*(-1.0 - r); N6t = 0.5*(-1.0 - r)
                Nr = new_matrix(3, 6)
                Nr%at(1, :) = [N1r, N2r, N3r, N4r, N5r, N6r]
                Nr%at(2, :) = [N1s, N2s, N3s, N4s, N5s, N6s]
                Nr%at(3, :) = [N1t, N2t, N3t, N4t, N5t, N6t]
            case (E3D8)
                N1r = 0.125*(-1.0)*(1.0 - s)*(1.0 - t); N1s = 0.125*(1.0 - r)*(-1.0)*(1.0 - t); N1t = 0.125*(1.0 - r)*(1.0 - s)*(-1.0)
                N2r = 0.125*(+1.0)*(1.0 - s)*(1.0 - t); N2s = 0.125*(1.0 + r)*(-1.0)*(1.0 - t); N2t = 0.125*(1.0 + r)*(1.0 - s)*(-1.0)
                N3r = 0.125*(+1.0)*(1.0 + s)*(1.0 - t); N3s = 0.125*(1.0 + r)*(+1.0)*(1.0 - t); N3t = 0.125*(1.0 + r)*(1.0 + s)*(-1.0)
                N4r = 0.125*(-1.0)*(1.0 + s)*(1.0 - t); N4s = 0.125*(1.0 - r)*(+1.0)*(1.0 - t); N4t = 0.125*(1.0 - r)*(1.0 + s)*(-1.0)
                N5r = 0.125*(-1.0)*(1.0 - s)*(1.0 + t); N5s = 0.125*(1.0 - r)*(-1.0)*(1.0 + t); N5t = 0.125*(1.0 - r)*(1.0 - s)*(+1.0)
                N6r = 0.125*(+1.0)*(1.0 - s)*(1.0 + t); N6s = 0.125*(1.0 + r)*(-1.0)*(1.0 + t); N6t = 0.125*(1.0 + r)*(1.0 - s)*(+1.0)
                N7r = 0.125*(+1.0)*(1.0 + s)*(1.0 + t); N7s = 0.125*(1.0 + r)*(+1.0)*(1.0 + t); N7t = 0.125*(1.0 + r)*(1.0 + s)*(+1.0)
                N8r = 0.125*(-1.0)*(1.0 + s)*(1.0 + t); N8s = 0.125*(1.0 - r)*(+1.0)*(1.0 + t); N8t = 0.125*(1.0 - r)*(1.0 + s)*(+1.0)
                Nr = new_matrix(3, 8)
                Nr%at(1, :) = [N1r, N2r, N3r, N4r, N5r, N6r, N7r, N8r]
                Nr%at(2, :) = [N1s, N2s, N3s, N4s, N5s, N6s, N7s, N8s]
                Nr%at(3, :) = [N1t, N2t, N3t, N4t, N5t, N6t, N7t, N8t]
            case default
                error stop ERROR_UNDEFINED_ELEMENT_TYPE
        end select
    end function
    
end module
