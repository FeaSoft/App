! Description:
! Definition of a finite element mesh.
module m_mesh
    use m_node
    use m_element
    implicit none
    
    private
    public t_mesh, new_mesh
    
    type t_mesh
        integer                      :: n_nodes     ! number of nodes
        integer                      :: n_elements  ! number of elements
        integer                      :: m_space     ! modeling space
        type(t_node),    allocatable :: nodes(:)    ! mesh nodes
        type(t_element), allocatable :: elements(:) ! mesh elements
    contains
        final :: destructor
    end type
    
    interface new_mesh
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Finite element mesh constructor.
    type(t_mesh) function constructor(n_nodes, n_elements, m_space) result(this)
        integer, intent(in) :: n_nodes    ! number of nodes
        integer, intent(in) :: n_elements ! number of elements
        integer, intent(in) :: m_space    ! modeling space
        this%n_nodes    = n_nodes
        this%n_elements = n_elements
        this%m_space    = m_space
        allocate(this%nodes(this%n_nodes))
        allocate(this%elements(this%n_elements))
    end function
    
    ! Description:
    ! Finite element mesh destructor.
    subroutine destructor(this)
        type(t_mesh), intent(inout) :: this
        if (allocated(this%nodes))    deallocate(this%nodes)
        if (allocated(this%elements)) deallocate(this%elements)
    end subroutine
    
end module
