! Description:
! Definition of a finite element.
module m_element
    use m_constants
    use m_node
    use m_section
    implicit none
    
    private
    public t_element, new_element, E2D3, E2D4, E3D4, E3D5, E3D6, E3D8, ERROR_UNDEFINED_ELEMENT_TYPE
    
    ! available finite element types
    integer, parameter :: E2D3 = 11, & ! 2D interpolation element with 3 nodes
                          E2D4 = 12, & ! 2D interpolation element with 4 nodes
                          E3D4 = 13, & ! 3D interpolation element with 4 nodes
                          E3D5 = 14, & ! 3D interpolation element with 5 nodes
                          E3D6 = 15, & ! 3D interpolation element with 6 nodes
                          E3D8 = 16    ! 3D interpolation element with 8 nodes
    
    ! error messages
    character(*), parameter :: ERROR_UNDEFINED_ELEMENT_TYPE = 'Error: undefined element type'
    
    type t_element
        character(4)         :: t_name     ! name of element type
        integer              :: t_element  ! type of element
        integer              :: n_nodes    ! number of nodes
        integer              :: n_ndofs    ! number of nodal DOFs
        integer              :: n_edofs    ! number of element DOFs
        integer              :: n_ips      ! number of integration points
        integer              :: i_section  ! index of section
        integer, allocatable :: i_nodes(:) ! index of nodes
        integer, allocatable :: dofs(:)    ! algebraic connectivity (positive number: active DOF; negative number: inactive DOF)
    contains
        procedure :: compute_surface_normal, compute_surface_area
        final     :: destructor
    end type
    
    interface new_element
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Finite element constructor.
    type(t_element) function constructor(t_element, i_section) result(self)
        integer, intent(in) :: t_element ! type of element
        integer, intent(in) :: i_section ! index of section
        self%t_element = t_element
        self%i_section = i_section
        
        ! name of element type based on element type
        select case (self%t_element)
            case (E2D3); self%t_name = 'E2D3'
            case (E2D4); self%t_name = 'E2D4'
            case (E3D4); self%t_name = 'E3D4'
            case (E3D5); self%t_name = 'E3D5'
            case (E3D6); self%t_name = 'E3D6'
            case (E3D8); self%t_name = 'E3D8'
            case default; error stop ERROR_UNDEFINED_ELEMENT_TYPE
        end select
        
        ! number of element nodes based on element type
        select case (self%t_element)
            case (E2D3); self%n_nodes = 3
            case (E2D4); self%n_nodes = 4
            case (E3D4); self%n_nodes = 4
            case (E3D5); self%n_nodes = 5
            case (E3D6); self%n_nodes = 6
            case (E3D8); self%n_nodes = 8
            case default; error stop ERROR_UNDEFINED_ELEMENT_TYPE
        end select
        
        ! number of nodal DOFs based on element type
        select case (self%t_element)
            case (E2D3); self%n_ndofs = 2 ! UX, UY
            case (E2D4); self%n_ndofs = 2 ! UX, UY
            case (E3D4); self%n_ndofs = 3 ! UX, UY, UZ
            case (E3D5); self%n_ndofs = 3 ! UX, UY, UZ
            case (E3D6); self%n_ndofs = 3 ! UX, UY, UZ
            case (E3D8); self%n_ndofs = 3 ! UX, UY, UZ
            case default; error stop ERROR_UNDEFINED_ELEMENT_TYPE
        end select
        
        ! number of element DOFs
        self%n_edofs = self%n_nodes * self%n_ndofs
        
        ! number of integration points based on element type
        select case (self%t_element)
            case (E2D3); self%n_ips = 1
            case (E2D4); self%n_ips = 4
            case (E3D4); self%n_ips = 1
            case (E3D5); self%n_ips = 5
            case (E3D6); self%n_ips = 6
            case (E3D8); self%n_ips = 8
            case default; error stop ERROR_UNDEFINED_ELEMENT_TYPE
        end select
        
        ! allocate arrays
        allocate(self%i_nodes(self%n_nodes))
        allocate(self%dofs(self%n_edofs))
    end function
    
    ! Description:
    ! Finite element destructor.
    subroutine destructor(self)
        type(t_element), intent(inout) :: self
        if (allocated(self%i_nodes)) deallocate(self%i_nodes)
        if (allocated(self%dofs))    deallocate(self%dofs)
    end subroutine
    
    ! Description:
    ! Compute element surface normal.
    subroutine compute_surface_normal(self, nodes, array)
        ! procedure arguments
        class(t_element), intent(in)    :: self     ! this element
        type(t_node),     intent(in)    :: nodes(:) ! surface nodes
        real,             intent(inout) :: array(:) ! results
        
        ! additional variables
        real :: nix, niy, niz    ! vector components
        real :: njx, njy, njz    ! vector components
        real :: nkx, nky, nkz    ! vector components
        real :: vecA(3), vecB(3) ! temporary arrays
        
        select case (self%n_ndofs)
            case (2)
                nix = nodes(1)%coordinates(1); niy = nodes(1)%coordinates(2)
                njx = nodes(2)%coordinates(1); njy = nodes(2)%coordinates(2)
                ! cross product
                array(1:2) = [njy - niy, nix - njx]
                ! normalize
                array(1:2) = array(1:2)/norm2(array(1:2))
            case (3)
                nix = nodes(1)%coordinates(1); niy = nodes(1)%coordinates(2); niz = nodes(1)%coordinates(3)
                njx = nodes(2)%coordinates(1); njy = nodes(2)%coordinates(2); njz = nodes(2)%coordinates(3)
                nkx = nodes(3)%coordinates(1); nky = nodes(3)%coordinates(2); nkz = nodes(3)%coordinates(3)
                vecA(1:3) = [njx - nix, njy - niy, njz - niz]
                vecB(1:3) = [nkx - njx, nky - njy, nkz - njz]
                ! cross product
                array(1) = vecA(2)*vecB(3) - vecA(3)*vecB(2)
                array(2) = vecA(3)*vecB(1) - vecA(1)*vecB(3)
                array(3) = vecA(1)*vecB(2) - vecA(2)*vecB(1)
                ! normalize
                array(1:3) = array(1:3)/norm2(array(1:3))
        end select
    end subroutine
    
    ! Description:
    ! Compute element surface area.
    real function compute_surface_area(self, nodes, section) result(A)
        ! procedure arguments
        class(t_element), intent(in) :: self     ! this element
        type(t_node),     intent(in) :: nodes(:) ! surface nodes
        type(t_section),  intent(in) :: section  ! element section
        
        ! additional variables
        real :: L, R             ! length and radius
        real :: u(3), v(3), w(3) ! auxiliary vectors
        
        select case (self%n_ndofs)
            case (2) ! surface is a line
                L = norm2(nodes(1)%coordinates(:) - nodes(2)%coordinates(:))
                select case (section%t_section)
                    case (CPS, CPE)
                        A = L*section%thickness
                    case (CAX)
                        R = (nodes(1)%coordinates(1) + nodes(2)%coordinates(1))/2.0 ! (x1 + x2)/2
                        A = L*2.0*PI*R
                    case default; error stop ERROR_UNDEFINED_SECTION_TYPE
                end select
            case (3) ! surface is a polygon
                select case (size(nodes))
                    case (3) ! surface is a triangle
                        u = nodes(2)%coordinates(:) - nodes(1)%coordinates(:)
                        v = nodes(3)%coordinates(:) - nodes(1)%coordinates(:)
                        ! cross product
                        w(1) = u(2)*v(3) - u(3)*v(2)
                        w(2) = u(3)*v(1) - u(1)*v(3)
                        w(3) = u(1)*v(2) - u(2)*v(1)
                        ! area
                        A = norm2(w)/2.0
                    case (4) ! surface is a quad
                        ! compute area of first triangle:
                            u = nodes(2)%coordinates(:) - nodes(1)%coordinates(:)
                            v = nodes(3)%coordinates(:) - nodes(1)%coordinates(:)
                            ! cross product
                            w(1) = u(2)*v(3) - u(3)*v(2)
                            w(2) = u(3)*v(1) - u(1)*v(3)
                            w(3) = u(1)*v(2) - u(2)*v(1)
                            ! area
                            A = norm2(w)/2.0
                        ! compute area of second triangle:
                            u = nodes(3)%coordinates(:) - nodes(1)%coordinates(:)
                            v = nodes(4)%coordinates(:) - nodes(1)%coordinates(:)
                            ! cross product
                            w(1) = u(2)*v(3) - u(3)*v(2)
                            w(2) = u(3)*v(1) - u(1)*v(3)
                            w(3) = u(1)*v(2) - u(2)*v(1)
                            ! area
                            A = A + norm2(w)/2.0
                end select
        end select
    end function
    
end module
