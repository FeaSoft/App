! Description:
! Definition of a finite element.
module m_element
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
        final :: destructor
    end type
    
    interface new_element
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Finite element constructor.
    type(t_element) function constructor(t_element, i_section) result(this)
        integer, intent(in) :: t_element ! type of element
        integer, intent(in) :: i_section ! index of section
        this%t_element = t_element
        this%i_section = i_section
        
        ! name of element type based on element type
        select case (this%t_element)
            case (E2D3); this%t_name = 'E2D3'
            case (E2D4); this%t_name = 'E2D4'
            case (E3D4); this%t_name = 'E3D4'
            case (E3D5); this%t_name = 'E3D5'
            case (E3D6); this%t_name = 'E3D6'
            case (E3D8); this%t_name = 'E3D8'
            case default; error stop ERROR_UNDEFINED_ELEMENT_TYPE
        end select
        
        ! number of element nodes based on element type
        select case (this%t_element)
            case (E2D3); this%n_nodes = 3
            case (E2D4); this%n_nodes = 4
            case (E3D4); this%n_nodes = 4
            case (E3D5); this%n_nodes = 5
            case (E3D6); this%n_nodes = 6
            case (E3D8); this%n_nodes = 8
            case default; error stop ERROR_UNDEFINED_ELEMENT_TYPE
        end select
        
        ! number of nodal DOFs based on element type
        select case (this%t_element)
            case (E2D3); this%n_ndofs = 2 ! UX, UY
            case (E2D4); this%n_ndofs = 2 ! UX, UY
            case (E3D4); this%n_ndofs = 3 ! UX, UY, UZ
            case (E3D5); this%n_ndofs = 3 ! UX, UY, UZ
            case (E3D6); this%n_ndofs = 3 ! UX, UY, UZ
            case (E3D8); this%n_ndofs = 3 ! UX, UY, UZ
            case default; error stop ERROR_UNDEFINED_ELEMENT_TYPE
        end select
        
        ! number of element DOFs
        this%n_edofs = this%n_nodes * this%n_ndofs
        
        ! number of integration points based on element type
        select case (this%t_element)
            case (E2D3); this%n_ips = 1
            case (E2D4); this%n_ips = 4
            case (E3D4); this%n_ips = 1
            case (E3D5); this%n_ips = 5
            case (E3D6); this%n_ips = 6
            case (E3D8); this%n_ips = 8
            case default; error stop ERROR_UNDEFINED_ELEMENT_TYPE
        end select
        
        ! allocate arrays
        allocate(this%i_nodes(this%n_nodes))
        allocate(this%dofs(this%n_edofs))
    end function
    
    ! Description:
    ! Finite element destructor.
    subroutine destructor(this)
        type(t_element), intent(inout) :: this
        if (allocated(this%i_nodes)) deallocate(this%i_nodes)
        if (allocated(this%dofs))    deallocate(this%dofs)
    end subroutine
    
end module
